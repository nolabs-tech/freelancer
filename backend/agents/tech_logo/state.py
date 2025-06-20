from typing import TypedDict, List, Dict, Any, Optional

# ==================== STATE DEFINITION ====================
class LogoDesignState(TypedDict):
    """Central state shared across all agents"""
    
    # User interaction
    user_input: str
    conversation_history: List[Dict[str, str]]
    user_feedback: Optional[str]
    iteration_count: int
    
    # Agent outputs
    chat_summary: Optional[str]
    design_concepts: Optional[List[Dict[str, Any]]]
    generated_logos: Optional[List[Dict[str, Any]]]
    ranking_results: Optional[Dict[str, Any]]
    final_package: Optional[str]
    generation_attempts: Optional[int]
    
    # Control flow
    current_step: str
    needs_regeneration: bool
    user_approved: bool
    error_message: Optional[str]
    
    # Technical data
    client_requirements: Optional[Dict[str, Any]]
    generation_attempts: int
    max_attempts: int