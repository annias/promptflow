"""
Returns a list of quotes ordered based on their coverage type and price.
Quotes are bucketed by coverage type then sorted in each bucket by price 
from least expensive to most expensive.

This endpoint will return an error if the quote object is incomplete in
some way.
"""
from typing import Optional
import requests
from pydantic import BaseModel

from itk_interface.common import get_base_url


class QuoteResultCompany(BaseModel):
    name: str
    logo_url: Optional[str]


class QuoteResultRate(BaseModel):
    annual_premium: float
    face_amount: float
    is_quoted_by_premium: bool
    limited_pay_constraint: str
    monthly_premium: float
    rate_type: str


class QuoteResult(BaseModel):
    id: int
    company: QuoteResultCompany
    rates: list[QuoteResultRate]
    coverage_type_id: int
    is_covered: bool
    plan_name: str
    why_reasons: list[str]
    quote: str
    timestamp: str
    compensation_warning: Optional[str]
    eapp_link: Optional[str]
    effective_date: Optional[str]
    house_hold_discount: Optional[str]
    policy_fee: Optional[str]
    is_social_security_billing_supported: Optional[bool]
    plan_info: Optional[list[str]]
    underwriting_warning: Optional[str]


def get_quote_results(id: int) -> list[QuoteResult]:
    return requests.get(f"{get_base_url()}/quote/results/", json={"id": id}).json()
