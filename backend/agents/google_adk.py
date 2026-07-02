from typing import List, Dict, Any, Callable

class SessionState:
    """
    SessionState represents the shared state passed between agents in Google ADK.
    It stores intermediate outputs and context.
    """
    def __init__(self, initial_data: Dict[str, Any] = None):
        self._state = initial_data or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any):
        self._state[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return self._state.copy()


class Agent:
    """
    Agent is the primary block in Google ADK, encapsulating a specific persona,
    instructions, and local tools (skills).
    """
    def __init__(self, name: str, instruction: str, tools: List[Callable] = None, model: str = "gemini-2.5-flash"):
        self.name = name
        self.instruction = instruction
        self.tools = tools or []
        self.model = model

    def run(self, prompt: str, session_state: SessionState = None) -> str:
        """
        Executes the agent logic. In this simulated environment, this runs 
        completely offline by combining instructions and tools to produce a response.
        """
        if session_state is None:
            session_state = SessionState()
        
        # Log agent activation in state for auditing
        history = session_state.get("history", [])
        history.append(f"Activated: Agent '{self.name}' using model '{self.model}'")
        session_state.set("history", history)
        
        # In a real ADK, the agent invokes LLMs and tools dynamically.
        # In our offline simulation, we call the agent's core capability method.
        # The Coordinator and other agents override/extend this behavior.
        return self._execute_simulation(prompt, session_state)

    def _execute_simulation(self, prompt: str, session_state: SessionState) -> str:
        """Fallback simulation logic - to be overridden by specialized agents."""
        return f"[{self.name}] Acknowledged: '{prompt}'. (Offline execution template)"


class SequentialAgent(Agent):
    """
    SequentialAgent runs multiple agents in series, passing the output of 
    one agent as the context/input for the next agent.
    """
    def __init__(self, name: str, agents: List[Agent], instruction: str = ""):
        super().__init__(name=name, instruction=instruction, tools=[])
        self.agents = agents

    def run(self, prompt: str, session_state: SessionState = None) -> str:
        if session_state is None:
            session_state = SessionState()
            
        current_input = prompt
        history = session_state.get("history", [])
        history.append(f"Workflow '{self.name}' starting sequential chain of {len(self.agents)} agents.")
        session_state.set("history", history)
        
        for idx, agent in enumerate(self.agents):
            history = session_state.get("history", [])
            history.append(f"Workflow Step {idx+1}/{len(self.agents)}: Executing agent '{agent.name}'")
            session_state.set("history", history)
            
            # Run individual agent
            output = agent.run(current_input, session_state)
            
            # Save step output to session state
            session_state.set(f"{agent.name}_output", output)
            
            # Pass output to next step
            current_input = output
            
        return current_input
