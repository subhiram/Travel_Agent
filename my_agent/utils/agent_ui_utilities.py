from langgraph.types import interrupt
from my_agent.utils.state import HumanInterrupt, HumanInterruptConfig, HumanResponse
import json
from collections import defaultdict

# use the below function when using the agent chat ui
def get_human_feedback(query: str):
    """Use this function to get the user input"""
    print("[INTERRUPT] Triggering user input with query:", query)
    modified_query = {"question": query}
    interrupt_request: HumanInterrupt = {
        "action_request": {
            "action": "Human assistance required.",
            "args": modified_query,
        },
        "config": {
            "allow_ignore": False,
            "allow_respond": True,
            "allow_edit": False,
            "allow_accept": False,
        },
    }
    response: HumanResponse = interrupt([interrupt_request])[0]
    print("[INTERRUPT] Received response:", response)
    print("The response is ",response)
    print("type of response:", type(response))
    return response["args"]