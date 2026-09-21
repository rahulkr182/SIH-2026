import os
from typing_extensions import TypedDict
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.sandbox.docker_runner import run_sandboxed_code

class AgentState(TypedDict):
    modality: str
    prompt: str
    file_name: Optional[str]
    plan: Optional[str]
    code_to_execute: Optional[str]
    sandbox_output: Optional[str]
    rag_context: Optional[str]
    vision_context: Optional[str]
    pdf_edits: Optional[str]
    draft: Optional[str]
    trace: List[str]

# Initialize LLM - uses OpenAI, Groq, or local vLLM/Ollama via base_url
llm_kwargs = {
    "model": os.getenv("MODEL_NAME", "qwen2.5-coder:1.5b"),
    "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
    "temperature": 0.1
}
api_base = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
if api_base:
    llm_kwargs["base_url"] = api_base

llm = ChatOpenAI(**llm_kwargs)

# Initialize Vision LLM (default to llava for images)
vision_llm_kwargs = {
    "model": os.getenv("VISION_MODEL_NAME", "llava:7b"),
    "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
    "temperature": 0.1
}
if api_base:
    vision_llm_kwargs["base_url"] = api_base
vision_llm = ChatOpenAI(**vision_llm_kwargs)

def vision_node(state: AgentState) -> dict:
    file_path = state.get('file_name')
    if not file_path or not os.path.exists(file_path):
        state['trace'].append("No readable document found.")
        return {"vision_context": "No readable document found.", "trace": state['trace']}
        
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.png', '.jpg', '.jpeg']:
        state['trace'].append(f"Detected Image ({ext}). Sending to Vision Model...")
        try:
            import base64
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Extract all text and describe this image in detail."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}
                ]
            )
            response = vision_llm.invoke([message])
            text = response.content
            state['trace'].append(f"Vision extraction complete. Read {len(text)} characters.")
            return {"vision_context": text.strip(), "trace": state['trace']}
        except Exception as e:
            state['trace'].append(f"Vision extraction failed: {str(e)}")
            return {"vision_context": f"Error processing image: {str(e)}", "trace": state['trace']}
            
    else:
        state['trace'].append(f"Detected Document ({ext}). Parsing text...")
        try:
            import fitz
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            state['trace'].append(f"Document extraction complete. Read {len(text)} characters.")
            return {"vision_context": text.strip(), "trace": state['trace']}
        except Exception as e:
            state['trace'].append(f"Document extraction failed: {str(e)}")
            return {"vision_context": f"Error reading document: {str(e)}", "trace": state['trace']}

def planner_node(state: AgentState) -> dict:
    state['trace'].append("Planning task execution...")
    
    prompt = f"""You are the planning agent for an industrial AI workbench.
Task Modality: {state['modality']}
User Prompt: {state['prompt']}
Extracted Document Content: {state.get('vision_context', 'None')}

Determine the execution path.
1. If the prompt asks to edit, redact, or replace text in the uploaded document, output exactly 'REQUIRES_EDIT'.
2. If the prompt requires safety math or calculation, output exactly 'REQUIRES_MATH'.
3. If the prompt asks about safety regulations, retirement thickness, or pipeline rules, output exactly 'REQUIRES_RAG'.
4. Otherwise, output 'NO_MATH'.
Respond with ONLY the exact string from the options above. Do not include any other text."""

    response = llm.invoke([HumanMessage(content=prompt)])
    plan = response.content.strip()
    state['trace'].append(f"Plan decided: {plan}")
    return {"plan": plan, "trace": state['trace']}

def coder_node(state: AgentState) -> dict:
    state['trace'].append("Generating Python code for math execution...")
    
    prompt = f"""You are an expert Python engineer. 
Write a simple Python script to solve the following task. 
Use print() to output the final answer. DO NOT use markdown formatting, just return raw python code.
Task: {state['prompt']}"""

    response = llm.invoke([SystemMessage(content="Return only valid, raw python code. No markdown code blocks."), HumanMessage(content=prompt)])
    code = response.content.replace("```python", "").replace("```", "").strip()
    
    state['trace'].append("Code generated. Sending to Docker Sandbox...")
    return {"code_to_execute": code, "trace": state['trace']}

def sandbox_node(state: AgentState) -> dict:
    code = state['code_to_execute']
    if not code:
        return {"sandbox_output": "No code executed.", "trace": state['trace']}
        
    state['trace'].append("Executing code in air-gapped Docker sandbox...")
    result = run_sandboxed_code(code)
    
    if result['success']:
        output = f"Sandbox Success:\n{result['stdout']}"
        state['trace'].append("Sandbox execution successful.")
    else:
        output = f"Sandbox Error:\n{result['stderr']}"
        state['trace'].append("Sandbox execution failed.")
        
    return {"sandbox_output": output, "trace": state['trace']}

def rag_node(state: AgentState) -> dict:
    state['trace'].append("Querying Sovereign Qdrant DB for relevant SOPs...")
    from app.rag.query import search_sops
    
    context = search_sops(state['prompt'])
    state['trace'].append("SOP context retrieved from Vector DB.")
    return {"rag_context": context, "trace": state['trace']}

def editor_node(state: AgentState) -> dict:
    state['trace'].append("Parsing edits and directly modifying original PDF...")
    file_path = state.get('file_name')
    if not file_path or not file_path.lower().endswith('.pdf'):
        state['trace'].append("No PDF provided for editing.")
        return {"pdf_edits": "Failed: No PDF", "trace": state['trace']}
        
    prompt = f"""You are a precise JSON generator. The user wants to edit a PDF document.
User Prompt: {state['prompt']}
Extracted Document Content: {state.get('vision_context', 'None')}

Return a valid JSON array of objects representing the text replacements to make.
Each object must have exactly two keys: "old" (the exact text to find) and "new" (the replacement text).
Example:
[ {{"old": "Rahul Kumar", "new": "John Doe"}} ]
Output ONLY the raw JSON array. Do NOT wrap in markdown blocks.
"""
    response = llm.invoke([SystemMessage(content="Return only valid JSON array."), HumanMessage(content=prompt)])
    import json
    try:
        json_str = response.content.strip().replace('```json','').replace('```','')
        edits = json.loads(json_str)
        import fitz
        doc = fitz.open(file_path)
        changes_made = 0
        for edit in edits:
            old_text = edit.get('old')
            new_text = edit.get('new')
            if old_text and new_text:
                for page in doc:
                    rects = page.search_for(old_text)
                    for rect in rects:
                        page.add_redact_annot(rect, text=new_text, fill=(1,1,1), text_color=(0,0,0))
                        changes_made += 1
                    page.apply_redactions()
                    
        os.makedirs("data/outputs", exist_ok=True)
        doc.save("data/outputs/edited_document.pdf")
        state['trace'].append(f"Successfully applied {changes_made} redactions to original PDF.")
        return {"pdf_edits": f"Made {changes_made} edits", "trace": state['trace']}
    except Exception as e:
        state['trace'].append(f"Failed to edit PDF: {str(e)}")
        return {"pdf_edits": f"Error: {str(e)}", "trace": state['trace']}

def drafter_node(state: AgentState) -> dict:
    state['trace'].append("Drafting final deliverable memo...")
    
    prompt = f"""You are an expert industrial engineering AI.
Write a clear, professional summary answering the user's prompt.
User Prompt: {state['prompt']}

If a document was analyzed by the vision model, here is the extracted text:
{state.get('vision_context', 'None')}

If the document was natively edited, here is the status:
{state.get('pdf_edits', 'None')}
If edited successfully, you MUST tell the user exactly this: "I have edited the original PDF document directly. Please click the **'Export Response to PDF'** button below to download your modified document!"

If math was executed, here is the sandbox output:
{state.get('sandbox_output', 'None')}

If internal regulations were searched, here is the retrieved SOP context. You MUST explicitly cite these documents if provided:
{state.get('rag_context', 'None')}

Format beautifully in Markdown. CRITICAL INSTRUCTION: Keep your response extremely concise and strictly to the point (no more than 3-4 sentences). Do NOT generate long manual calculations. If math was required, only report the sandbox output. If no sandbox output is present, provide a direct one-sentence answer."""

    response = llm.invoke([HumanMessage(content=prompt)])
    state['trace'].append("Deliverable drafted successfully.")
    
    return {"draft": response.content, "trace": state['trace']}
