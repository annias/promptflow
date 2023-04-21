"""
Where answers to questions can be submitted to the Quote Object.

When an Underwriting Item is added to the Quote Object, a list of
unanswered questions also get added. As long as there are unanswered
questions within the Quote Object, the quote cannot be run.
"""
import requests
from pydantic import BaseModel
from enum import Enum
from typing import Optional

from itk_interface.common import get_base_url


class QuestionType(str, Enum):
    radio_list = "radio_list"
    yes_no = "yes_no"
    date = "date"
    select = "select"


class Question(BaseModel):
    id: str
    type: QuestionType
    order: int
    prompt: str
    options: list[str]
    is_indication: bool
    is_second_level_indication: bool
    required: bool
    should_show: bool
    answer: Optional[str]


def get_question(id: int) -> Question:
    return requests.get(
        f"{get_base_url()}/quote/uw-entry/question/", json={"id": id}
    ).json()


def submit_answer(id: int, answer: str) -> Question:
    return requests.post(
        f"{get_base_url()}/quote/uw-entry/question/", json={"id": id, "answer": answer}
    ).json()
