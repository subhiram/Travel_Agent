from langchain_core.tools import tool
from langgraph.types import interrupt
from my_agent.utils.state import HumanInterrupt, HumanInterruptConfig, HumanResponse

@tool
def human_assistance_bk(query: str):
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

@tool
def human_assistance(query: str):
    """Use this function to get the user input"""
    print("[INTERRUPT] Triggering user input with query in tool:", query)
    return interrupt(
        HumanInterrupt(
            action_request={
                "action": "Human",
                "args": {"question": query}
            },
            config={
                "allow_ignore": False,
                "allow_respond": True,
                "allow_edit": False,
                "allow_accept": False,
            }
        )
    )

# --- old code ---------
# @tool
# def human_assistance(query: str):
#     """Use this function to get the user input"""
#     print("[INTERRUPT] Triggering user input with query:", query)
#     modified_query = {"question": query}
#     interrupt_request: HumanInterrupt = {
#         "action_request": {
#             "action": "Human assistance required.",
#             "args": modified_query,
#         },
#         "config": {
#             "allow_ignore": False,
#             "allow_respond": True,
#             "allow_edit": False,
#             "allow_accept": False,
#         },
#     }
#     response: HumanResponse = interrupt([interrupt_request])[0]
#     print("[INTERRUPT] Received response:", response)
#     print("The response is ",response)
#     print("type of response:", type(response))
#     return response["args"]

# --------- sandbox code ---------
# def human_assistance(query: str):
#     """Use this function to get the user input"""
#     print("[INTERRUPT] Triggering user input with query in tool:", query)
#     return interrupt(
#         HumanInterrupt(
#             action_request={
#                 "action": "Human",
#                 "args": {"question": query}
#             },
#             config={
#                 "allow_ignore": False,
#                 "allow_respond": True,
#                 "allow_edit": False,
#                 "allow_accept": False,
#             }
#         )
#     )

tools = [human_assistance]