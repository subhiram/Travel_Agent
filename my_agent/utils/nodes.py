from functools import lru_cache
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from my_agent.utils.pydantic_classes import is_given_stentence_a_question, lead_details
from my_agent.utils.prompts import system_prompt, question_classifier_prompt, lead_details_extractor_prompt
from langgraph.graph import StateGraph, END
from typing import Literal
from my_agent.utils.agent_ui_utilities import get_human_feedback
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import SystemMessage

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

def should_continue_phase1_conversation(state) -> str:
    """
    This function is used to determine if the agent should continue the conversation or not.
    """
    print("state: ", state)
    if state.get("phase1_conversation_complete") is True:
        return "collect_user_details"
    else:
        return "end"

def collect_user_details(state):
    print("Collecting user details node called")
    # collect the users name, email, phone number to create a lead
    # ask for user's name
    print("state: ", state)
    state["messages"].append(AIMessage(content="Entered the collect_user_details node"))
    name = get_human_feedback(query="Can you please provide your name?")
    print("type of name:", type(name))
    state["user_name"] = name
    email = get_human_feedback(query="Can you please provide your email?")
    state["user_email"] = email
    phone = get_human_feedback(query="Can you please provide your phone number?")
    state["user_phone"] = phone
    print("User details collected: ", name, email, phone)
    # create a lead with the user details
    # lead = create_lead(state["user_name"], state["user_email"], state["user_phone"])
    print("exiting collect_user_details node")
    return state