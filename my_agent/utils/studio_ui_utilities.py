from langgraph.types import interrupt
from my_agent.utils.state import HumanInterrupt, HumanInterruptConfig, HumanResponse


def get_human_feedback(query: str, context=None):
    """Use this function to get the user input"""
    if context:
        response = interrupt(
            {
                "context": context,
                "task": "Human assistance required.",
                "question": query
            }
        )
    else:
        response = interrupt(
            {
                "question": query
            }
        )
    print(response)
    print(type(response))
    if isinstance(response, dict) and response:
        print(next(iter(response.values())))
        return next(iter(response.values()))
    else:
        return response