from langchain_core.tools import tool
from langgraph.types import interrupt
from my_agent.utils.state import HumanInterrupt, HumanInterruptConfig, HumanResponse

@tool
def human_assistance(query: str):
    """Ask user for missing or unclear information."""
    response = interrupt(
        # Interrupt information to surface to the client.
        # Can be any JSON serializable value.
        {
            "task": "Human assistance required.",
            "llm's question": query
        }
    )
    if not response:
        return "not specified"
    return response


tools = [human_assistance]