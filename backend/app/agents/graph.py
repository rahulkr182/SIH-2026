from langgraph.graph import StateGraph, START, END
from app.agents.nodes import AgentState, planner_node, coder_node, sandbox_node, drafter_node, rag_node, vision_node

def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("vision", vision_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("sandbox", sandbox_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("drafter", drafter_node)
    
    # Conditional routing from START
    def start_router(state: AgentState):
        if state.get("file_name"):
            return "vision"
        return "planner"
        
    workflow.add_conditional_edges(
        START,
        start_router,
        {"vision": "vision", "planner": "planner"}
    )
    
    workflow.add_edge("vision", "planner")
    
    # Conditional routing based on plan
    def route_plan(state: AgentState):
        plan_text = state.get("plan", "")
        if "REQUIRES_MATH" in plan_text:
            return "coder"
        elif "REQUIRES_RAG" in plan_text:
            return "rag"
        return "drafter"
        
    workflow.add_conditional_edges(
        "planner",
        route_plan,
        {"coder": "coder", "rag": "rag", "drafter": "drafter"}
    )
    
    workflow.add_edge("coder", "sandbox")
    workflow.add_edge("sandbox", "drafter")
    workflow.add_edge("rag", "drafter")
    workflow.add_edge("drafter", END)
    
    return workflow.compile()

app_graph = build_graph()
