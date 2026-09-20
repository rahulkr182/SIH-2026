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
    draft: Optional[str]
    trace: List[str]

# Initialize LLM - uses OpenAI, Groq, or local vLLM/Ollama via base_url
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "deepseek-r1-distill-14b"),
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    base_url=os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
    temperature=0.1
)

def vision_node(state: AgentState) -> dict:
    state['trace'].append("Simulating Vision model to extract text from document...")
    file_path = state.get('file_name')
    if not file_path or not os.path.exists(file_path):
        return {"vision_context": "No readable document found.", "trace": state['trace']}
        
    try:
        import fitz
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        state['trace'].append(f"Vision extraction complete. Read {len(text)} characters.")
        return {"vision_context": text.strip(), "trace": state['trace']}
    except Exception as e:
        state['trace'].append(f"Vision extraction failed: {str(e)}")
        return {"vision_context": f"Error reading document: {str(e)}", "trace": state['trace']}

def planner_node(state: AgentState) -> dict:
    state['trace'].append("Planning task execution...")
    
    prompt = f"""You are the planning agent for an industrial AI workbench.
Task Modality: {state['modality']}
User Prompt: {state['prompt']}
Extracted Document Content: {state.get('vision_context', 'None')}

Determine the execution path.
1. If the prompt requires safety math or calculation, output exactly 'REQUIRES_MATH'.
2. If the prompt asks about safety regulations, retirement thickness, or pipeline rules, output exactly 'REQUIRES_RAG'.
3. Otherwise, output 'NO_MATH'."""

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

def drafter_node(state: AgentState) -> dict:
    state['trace'].append("Drafting final deliverable memo...")
    
    prompt = f"""You are an expert industrial engineering AI.
Write a clear, professional summary answering the user's prompt.
User Prompt: {state['prompt']}

If a document was analyzed by the vision model, here is the extracted text:
{state.get('vision_context', 'None')}

If math was executed, here is the sandbox output:
{state.get('sandbox_output', 'None')}

If internal regulations were searched, here is the retrieved SOP context. You MUST explicitly cite these documents if provided:
{state.get('rag_context', 'None')}

Format beautifully in Markdown."""

    response = llm.invoke([HumanMessage(content=prompt)])
    state['trace'].append("Deliverable drafted successfully.")
    
    return {"draft": response.content, "trace": state['trace']}
