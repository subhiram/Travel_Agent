from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END
from my_agent.utils.nodes import call_model, collect_user_name, collect_user_email, collect_user_phone, should_continue_phase1_conversation, call_model_with_tools, tools_node, tools_router, ask_human_node
from my_agent.utils.state import AgentState


# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model_with_tools)
workflow.add_node("collect_user_name", collect_user_name)
workflow.add_node("collect_user_email", collect_user_email)
workflow.add_node("collect_user_phone", collect_user_phone)
workflow.add_node("action", tools_node)
# workflow.add_node("ask_human_node", ask_human_node)
# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    tools_router,
    {
        "action": "action",
        "collect_user_name": "collect_user_name"
    }
)
workflow.add_edge("action", "agent")
workflow.add_edge("collect_user_name", "collect_user_email")
workflow.add_edge("collect_user_email", "collect_user_phone")
workflow.add_edge("collect_user_phone", END)


# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
