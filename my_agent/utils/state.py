from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence, Any, Optional, Literal, Union, List
from my_agent.utils.pydantic_classes import lead_details

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    lead_details: Optional[lead_details]
    trip_summary: Optional[List[dict]]
    phase1_conversation_complete: bool
    user_name: Optional[str]
    user_email: Optional[str]
    user_phone: Optional[str]

class ActionRequest(TypedDict):
    action: str
    args: dict[str, Any]

class HumanInterruptConfig(TypedDict):
    allow_ignore: bool
    allow_respond: bool
    allow_edit: bool
    allow_accept: bool

class HumanInterrupt(TypedDict):
    action_request: ActionRequest
    config: HumanInterruptConfig
    description: Optional[str]

class HumanResponse(TypedDict):
    type: Literal['accept', 'ignore', 'response', 'edit']
    args: Union[None, str, ActionRequest]