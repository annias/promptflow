from promptflow.src.state import State

"""
{
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
}
"""

def main(state: State):
    import json
    # check to see if all fields filled
    try:
        r = json.loads(state.result)
    except json.decoder.JSONDecodeError:
        return False
    for key in r.keys():
        if r[key] is None:
            return False
    return True
