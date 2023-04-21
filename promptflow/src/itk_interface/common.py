"""
Handles common functions and data for the ITK interface.
"""
import os
from enum import Enum
from pydantic import BaseModel


class QuoteUwEntryQuestionnaire(BaseModel):
    questions: str
    is_complete: bool


class UwItem(BaseModel):
    id: int
    name: str


class QuoteUwEntry(BaseModel):
    id: str
    uw_item: UwItem
    questionnaire: QuoteUwEntryQuestionnaire
    was_auto_added: bool


class AmountType(str, Enum):
    face = "face"
    premium = "premium"


class CoverageType(str, Enum):
    level = "level"
    graded = "graded"
    guaranteed = "guaranteed"
    limited_pay = "limited_pay"


class TermLength(str, Enum):
    _10 = "10"
    _15 = "15"
    _20 = "20"
    _30 = "30"


class MedSuppPlanCode(str, Enum):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = "e"
    f = "f"
    hdf = "hdf"
    g = "g"
    hdg = "hdg"
    k = "k"
    l = "l"
    m = "m"
    n = "n"
    basic = "basic"
    hgih_deductible = "hgih_deductible"


class PaymentType(str, Enum):
    bank_draf_eft = "bank_draf_eft"
    direct_express = "direct_express"
    credit_card = "credit_card"
    debit_card = "debit_card"


class Sex(str, Enum):
    male = "male"
    female = "female"


class State(str, Enum):
    al = "al"
    ak = "ak"
    az = "az"
    ar = "ar"
    ca = "ca"
    co = "co"
    ct = "ct"
    de = "de"
    fl = "fl"
    ga = "ga"
    hi = "hi"
    id = "id"
    il = "il"
    in_ = "in"
    ia = "ia"
    ks = "ks"
    ky = "ky"
    la = "la"
    me = "me"
    md = "md"
    ma = "ma"
    mi = "mi"
    mn = "mn"
    ms = "ms"
    mo = "mo"
    mt = "mt"
    ne = "ne"
    nv = "nv"
    nh = "nh"
    nj = "nj"
    nm = "nm"
    ny = "ny"
    nc = "nc"
    nd = "nd"
    oh = "oh"
    ok = "ok"
    or_ = "or"
    pa = "pa"
    ri = "ri"
    sc = "sc"
    sd = "sd"
    tn = "tn"
    tx = "tx"
    ut = "ut"
    vt = "vt"
    va = "va"
    wa = "wa"
    wv = "wv"
    wi = "wi"
    wy = "wy"


class Tobacco(str, Enum):
    none = "none"
    cigarettes = "cigarettes"
    cigarettes_plus_other_nicotine_products = "cigarettes_plus_other_nicotine_products"
    occasional_pipe_or_cigar_use_only = "occasional_pipe_or_cigar_use_only"
    other_nicotine_products = "other_nicotine_products"


class Toolkit(str, Enum):
    medsupp = "medsupp"
    fex = "fex"
    term = "term"


def get_bearer_token() -> str:
    """
    Returns the bearer token for the ITK interface.
    """
    return os.environ["ITK_API_TOKEN"]


def get_header() -> dict:
    """
    Returns the header for the ITK interface.
    """
    return {"Authorization": "Bearer " + get_bearer_token()}


def get_base_url() -> str:
    """
    Returns the base url for the ITK interface.
    """
    return "https://api.insurancetoolkits.com/api/v1/"
