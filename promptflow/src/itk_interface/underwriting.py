"""
Appends a new Underwriting Item to the uw_entries array. The uw_item_id
is obtained from the /uw-item/ endpoint.

When an Underwriting Item is added, there is a chance that a combination 
will be triggered resulting in an additional Underwriting Item and question
chain being added to the list of entries. When this happens, a flag,
was_auto_added, will be set to true on the underwriting item. This auto 
added Underwriting Item can be removed on the client side without risking
inaccurate quote results.
"""
import requests
from pydantic import BaseModel
from itk_interface.common import (
    QuoteUwEntryQuestionnaire,
    Toolkit,
    UwItem,
    get_base_url,
)
from enum import Enum


class AddUwResponse(BaseModel):
    id: str
    uw_item: UwItem
    questionnaire: QuoteUwEntryQuestionnaire
    was_auto_added: bool


class DrugAndHealthQueryType(str, Enum):
    drug = "drug"
    medsupp = "medsupp"
    term = "term"


class DrugAndHealthQuery(BaseModel):
    type: DrugAndHealthQueryType
    toolkit: Toolkit
    name: str
    name_contains: str
    name_starts_with: str


def get_uw_item(id: int) -> UwItem:
    """Returns the specific Underwriting Item object by its ID."""
    return requests.get(f"{get_base_url()}/quote/uw-item/", json={"id": id}).json()


def add_uw_item(uw_item_id: int) -> AddUwResponse:
    """
    Appends a new Underwriting Item to the uw_entries array. The uw_item_id
    is obtained from the /uw-item/ endpoint.

    When an Underwriting Item is added, there is a chance that a combination
    will be triggered resulting in an additional Underwriting Item and
    question chain being added to the list of entries. When this happens,
    a flag, was_auto_added, will be set to true on the underwriting item.
    This auto added Underwriting Item can be removed on the client side
    without risking inaccurate quote results.
    """
    return requests.post(
        f"{get_base_url()}/quote/uw-item/", json={"uw_item_id": uw_item_id}
    ).json()


def remove_uw_item(uw_item_id: int) -> None:
    """
    Removes an Underwriting Item from the uw_entries array. The uw_item_id
    is obtained from the /uw-item/ endpoint.
    """
    requests.delete(f"{get_base_url()}/quote/uw-item/", json={"id": uw_item_id})


def search_uw_items(query: DrugAndHealthQuery) -> list[UwItem]:
    return requests.post(f"{get_base_url()}/quote/uw-item", json=query.dict())
