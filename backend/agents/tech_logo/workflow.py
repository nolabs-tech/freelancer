
from langgraph.graph import StateGraph, END
from agents.tech_logo.state import LogoDesignState
from agents.tech_logo.agents import LogoDesignAgents
from typing import TypedDict, List, Dict, Any, Optional
import asyncio


def create_logo_design_workflow():
    """Create the complete logo design workflow using LangGraph"""
    
    agents = LogoDesignAgents()
    
    # Define the workflow graph
    workflow = StateGraph(LogoDesignState)
    
    # Add nodes (agents)
    workflow.add_node("chat", agents.chat_agent)
    workflow.add_node("summary", agents.summary_agent)
    workflow.add_node("design", agents.designer_agent)
    workflow.add_node("generate", agents.generator_agent)
    workflow.add_node("ranking", agents.ranking_agent)
    workflow.add_node("feedback", agents.feedback_agent)
    workflow.add_node("package", agents.package_agent)
    
    # Define workflow edges and conditions
    workflow.add_conditional_edges(
        "chat",
        lambda state: state["current_step"],
        {
            "chat": "chat",      # Continue conversation
            "summary": "summary"  # Move to summary
        }
    )
    
    workflow.add_edge("summary", "design")
    workflow.add_edge("design", "generate")
    workflow.add_edge("generate", "ranking")
    
    workflow.add_conditional_edges(
        "ranking",
        lambda state: state["current_step"],
        {
            "regenerate": "generate",     # Regenerate if quality is poor
            "user_review": "feedback"     # Present to user for feedback
        }
    )
    
    workflow.add_conditional_edges(
        "feedback",
        lambda state: state["current_step"],
        {
            "design": "design",       # New design concepts needed
            "generate": "generate",   # Regenerate with modifications
            "package": "package"      # User approved, create package
        }
    )
    
    workflow.add_edge("package", END)
    
    # Set entry point
    workflow.set_entry_point("chat")
    
    return workflow.compile()

class LogoDesignOrchestrator:
    def __init__(self):
        self.agent = LogoDesignAgents()
        self.session_state: Dict[str, LogoDesignState] = {}

    def start_session(self, session_id: str) -> Dict[str, Any]:
        """Start a new design session, agent initiates the chat"""
        state: LogoDesignState = {
            "user_input": "",  # No user input initially
            "conversation_history": [],
            "user_feedback": None,
            "iteration_count": 0,
            "chat_summary": None,
            "design_concepts": None,
            "generated_logos": None,
            "ranking_results": None,
            "final_package": None,
            "generation_attempts": 0,
            "current_step": "chat",
            "needs_regeneration": False,
            "user_approved": False,
            "error_message": None,
            "client_requirements": None,
            "max_attempts": 3
        }

        # Initial synthetic agent message
        system_greeting = {
            "role": "assistant",
            "content": "👋 Hello! I’m Alex, your logo design assistant. Let's begin by understanding your brand. Can you tell me about your company, its industry, and your target audience?"
        }
        state["conversation_history"].append(system_greeting)
        
        self.session_state[session_id] = state
        return {"message": system_greeting["content"]}

    async def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        state = self.session_state.get(session_id)
        if not state:
            return {"error": "Session not found"}

        print(f"\n[USER MESSAGE] {user_message}")
        print(f"[STEP] Current Step: {state['current_step']}")
        
        state["user_input"] = user_message
        state["conversation_history"].append({"role": "user", "content": user_message})

        if state["current_step"] == "chat":
            state = self.agent.chat_agent(state)
            print("[STEP] Completed chat_agent")
            
            if state["current_step"] == "summary":
                print("[STEP] Moving to summary_agent")
                state = self.agent.summary_agent(state)

                print("[STEP] Moving to designer_agent")
                state = await self.agent.designer_agent(state)

                print("[STEP] Moving to generator_agent")
                state = await self.agent.generator_agent(state)

                print("[STEP] Moving to ranking_agent")
                state = self.agent.ranking_agent(state)

                print("[STEP] Moving to package_agent")
                state = self.agent.package_agent(state)
        
        # ... similarly log each step
        self.session_state[session_id] = state
        return {
            "conversation": state["conversation_history"],
            "current_step": state["current_step"]
        }