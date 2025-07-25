from functools import lru_cache
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from my_agent.utils.pydantic_classes import is_given_stentence_a_question, lead_details
from my_agent.utils.prompts import system_prompt, question_classifier_prompt, lead_details_extractor_prompt, system_prompt_with_tools, system_prompt_with_tools_1
from langgraph.graph import StateGraph, END
from typing import Literal
from my_agent.utils.agent_ui_utilities import get_human_feedback
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import SystemMessage
from my_agent.utils.general_utilities import is_valid_name, is_valid_email, is_valid_phone

@lru_cache(maxsize=4)
def _get_model():
    model = ChatOllama(model="llama3.1", temperature=0)
    return model

def _get_model_with_tools():
    model = ChatOllama(model="llama3.1", temperature=0)
    model = model.bind_tools(tools)
    return model

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


# Define the function that calls the model
def call_model(state):
    messages = state["messages"]
    messages = [SystemMessage(content=system_prompt)] + messages
    model = _get_model()
    response = model.invoke(messages)
    print(response)
    # Add today's date and time to the system prompt so that agent can undertand and respond accordingly
    # check if the response has summary or summarize, hthen we can get the details
    if "[Trip Summary]" in response.content:
        print("Summary found in the response")
    # check if the Agent has enough information to create a lead
        structured_llm = model.with_structured_output(lead_details)
        prompt = lead_details_extractor_prompt.invoke({"input": response.content})
        structured_output = structured_llm.invoke(prompt)
        print("Structured Output for lead details: ", structured_output)
        state["lead_details"] = structured_output
        state["phase1_conversation_complete"] = True
        return state
    else:
        print("No summary found in the response")
        # check if the response is a question
        structured_llm = model.with_structured_output(is_given_stentence_a_question)
        prompt = question_classifier_prompt.invoke({"input": response.content})
        structured_output = structured_llm.invoke(prompt)
        print("Structured Output: ", structured_output)
        # We return a list, because this will get added to the existing list
        state['phase1_conversation_complete'] = False
        state['messages'] = [response]
        return state

def call_model_with_tools(state):
    messages = state["messages"]
    messages = [SystemMessage(content=system_prompt_with_tools)] + messages
    model = _get_model_with_tools()  # Changed from _get_model to bind tools
    response = model.invoke(messages)
    print(response)

    # Check for summary
    if "[Trip Summary]" in response.content:
        print("Summary found in the response")
        structured_llm = model.with_structured_output(lead_details)
        prompt = lead_details_extractor_prompt.invoke({"input": response.content})
        structured_output = structured_llm.invoke(prompt)
        print("Structured Output for lead details: ", structured_output)
        state["lead_details"] = structured_output
        state["phase1_conversation_complete"] = True
        state["messages"] = state["messages"] + [response]
        return state

    # Otherwise, check if follow-up question is needed
    print("No summary found in the response")
    content_lower = response.content.lower()
    should_ask_question = (
        "?" in response.content or
        any(phrase in content_lower for phrase in [
            "need to know", "please specify", "can you tell me",
            "what", "which", "unclear", "missing", "please provide"
        ])
    )

    if should_ask_question:
        print("Making a forced tool call to ask user a question")
        tool_response = AIMessage(
            content="I need more information to continue.",
            tool_calls=[
                {
                    "name": "human_assistance",
                    "args": {"query": response.content.strip()},
                    "id": "forced_call_1"
                }
            ]
        )
        state["messages"] = state["messages"] + [tool_response]
        state["phase1_conversation_complete"] = False
        return state

    # If no summary and not a question, just proceed with the raw response
    state["messages"] = state["messages"] + [response]
    state["phase1_conversation_complete"] = False
    return state


def should_continue_phase1_conversation(state) -> str:
    """
    This function is used to determine if the agent should continue the conversation or not.
    """
    print("state: ", state)
    if state.get("phase1_conversation_complete") is True:
        return "collect_user_name"
    else:
        return "end"

def collect_user_name(state):
    print("Collecting user name node called")
    print("state: ", state)
    
    while True:
        name = get_human_feedback(query="Can you please provide your name?")
        if is_valid_name(name):
            state["user_name"] = name.strip()
            print("Valid name received:", name)
            break
        else:
            state["messages"].append(AIMessage(content="Invalid name, please try again"))
    
    print("exiting collect_user_name node")
    return state


def collect_user_email(state):
    print("Collecting user email node called")
    print("state: ", state)
    while True:
        email = get_human_feedback(query="Can you please provide your email?")
        if is_valid_email(email):
            state["user_email"] = email.strip()
            print("Valid email received:", email)
            break
        else:
            state["messages"].append(AIMessage(content="Invalid email, please try again"))
    print("exiting collect_user_email node")
    return state

def collect_user_phone(state):
    print("Collecting user phone node called")
    print("state: ", state)
    while True:
        phone = get_human_feedback(query="Can you please provide your phone number?")
        if is_valid_phone(phone):
            print("Valid phone number received:", phone.strip())
            state["user_phone"] = phone.strip()
            break
        else:
            pass
            # state["messages"].append(AIMessage(content="Invalid phone number, please try again"))
    print("exiting collect_user_phone node")
    return state

tools_node = ToolNode(tools)

def tools_router(state):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls) > 0:
        return "action"
    return "collect_user_name"
    
# add a node to create a lead in the database and capture the lead id

# To do 

# in the system prompt edit it in such a way that we are able to collect the starting location details
# also make sure the user gives the correct dates (not just the vague details like month or year)


# afeter collecting the user specific details the name, email and mobile number, we need to collect the following details
# 1. Package Type (eg. Full Package (Flights + Land), only flights, only land)
# 2. Flight Preferences (eg. Class, Economy, Business, First)
# 3. Accommodation Preferences (eg. Star Category, 2-star, 3-star, 4-star, 5-star)
# 4. Location Preference (eg. central london, outskirts)
# 5. Interests / Activities (eg. sightseeing, shopping, food, etc.)


# ----------- starting some sandbox code 

# def ask_human_node(state):
#     print("ask_human_node called")
#     print("state: ", state)

#     messages = state.get("messages", [])
#     last_message = messages[-1] if messages else None

#     if isinstance(last_message, AIMessage):
#         tool_calls = last_message.tool_calls or []

#         for tool_call in tool_calls:
#             if tool_call["name"] == "human_assistance":
#                 query = tool_call.get("args", {}).get("query", "Please provide input.")
#                 user_input = get_human_feedback(query=query)
#                 print("user_input: ", user_input)

#                 # Append user response as a HumanMessage
#                 messages.append(HumanMessage(content=user_input))

#                 state["messages"] = messages
#                 state["phase1_conversation_complete"] = False
#                 return state

#         print("No 'human_assistance' tool_call found in last AIMessage.")
#         return state

#     print("Last message is not an AIMessage.")
#     return state

def ask_human_node(state):
    print("ask_human_node called")
    print("state: ", state)

    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None

    if isinstance(last_message, AIMessage):
        print("Last message is an AIMessage.")
        print("last_message: ", last_message)
        # user_input = get_human_feedback(query=last_message.content)
        # print("user_input: ", user_input)
        # state["messages"].append(HumanMessage(content=user_input))
        # state["phase1_conversation_complete"] = False
        return interrupt(
            HumanInterrupt(
                action_request={
                    "action": "Human",
                    "args": {"question": last_message.content}
                },
                config={
                    "allow_ignore": False,
                    "allow_respond": True,
                    "allow_edit": False,
                    "allow_accept": False,
                }
            )
        )
        return state

    print("Last message is not an AIMessage.")
    return state




# ----------- ending some sandbox code 