from pydantic import BaseModel, Field
from typing import List, Optional

class is_given_stentence_a_question(BaseModel):
    """Given a sentence, determine if it is a question or not"""
    answer: bool = Field(description="Is the given sentence a question?")

class lead_details(BaseModel):
    """Lead details"""
    destination: str = Field(description="The destination of the trip")
    travel_date: str = Field(description="The travel date of the trip")
    duration: int = Field(description="The duration of the trip")
    number_of_adults: int = Field(description="The number of adults in the trip")
    number_of_children: int = Field(description="The number of children in the trip")
    travel_type: str = Field(description="The travel type of the trip")
    starting_location: str = Field(description="The starting location of the trip")