"""
Enter a client's information and receive back a list of quotes ordered based
on coverage and price.

The Quoting and Underwriting API is what we refer to as "conversational". 
Each quote starts as a session object containing only the toolkit in use. 
Information is then incrementally added to the Quote Object.

When an Underwriting Item (drug/health condition) is added to the quote, 
along with it underwriting questions are also added. Each question that is
answered and submitted to the API has the side effect of updating the state
of the Quote Object either by adding additional questions, marking certain
questions as hidden, or removing questions completely. The result is that
the client will have the necessary context to decide on how to show the
fewest questions required to run the quote accurately.
"""
from typing import Optional
import requests
from pydantic import BaseModel

from itk_interface.common import (
    QuoteUwEntry,
    AmountType,
    CoverageType,
    TermLength,
    MedSuppPlanCode,
    PaymentType,
    Sex,
    State,
    Tobacco,
    Toolkit,
    get_base_url,
)


class Quote(BaseModel):
    id: str
    age_in_years: Optional[int]
    height_in_inches: Optional[int]
    weight_in_pounds: Optional[int]
    created: str
    uw_entries: list[QuoteUwEntry]
    date_of_birth: Optional[str]
    amount: Optional[float]
    amount_type: Optional[AmountType]
    coverage_type: Optional[CoverageType]
    return_of_premium: Optional[bool]
    term_length: Optional[TermLength]
    med_supp_plan_code: Optional[MedSuppPlanCode]
    zipcode: Optional[str]  # <10 char
    payment_type: Optional[PaymentType]
    sex: Optional[Sex]
    state: Optional[State]
    tobacco: Optional[Tobacco]
    toolkit: Toolkit


class QuoteQuery(BaseModel):
    age_in_years: Optional[int]
    height_in_inches: Optional[int]
    weight_in_pounds: Optional[int]
    uw_entries: list[QuoteUwEntry]
    date_of_birth: Optional[str]
    amount: Optional[float]
    amount_type: Optional[AmountType]
    coverage_type: Optional[CoverageType]
    return_of_premium: Optional[bool]
    term_length: Optional[TermLength]
    med_supp_plan_code: Optional[MedSuppPlanCode]
    zipcode: Optional[str]  # <10 char
    payment_type: Optional[PaymentType]
    sex: Optional[Sex]
    state: Optional[State]
    tobacco: Optional[Tobacco]
    toolkit: Toolkit


def get_quote(id: str) -> Quote:
    """
    Get a quote by id.
    """
    return Quote.from_dict(
        requests.get(f"{get_base_url()}/quote/", json={"id": id}).json()
    )


def start_quote(query: QuoteQuery) -> Quote:
    """
    Start a new quote.
    """
    return Quote.from_dict(
        requests.post(f"{get_base_url()}/quote", json=query.dict()).json()
    )


def update_quote(id: str, query: QuoteQuery) -> Quote:
    """
    Update a quote.
    """
    return Quote.from_dict(
        requests.patch(f"{get_base_url()}/quote/{id}", json=query.dict()).json()
    )
