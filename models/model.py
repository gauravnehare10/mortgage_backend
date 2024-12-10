from pydantic import BaseModel
from typing import Optional, Dict, List

class User(BaseModel):
    name: str
    username: str
    email: str
    contactnumber: int
    password: str

class LoginModel(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_details: Optional[Dict[str, str]]
    mortgage: Optional[Dict[str, str]]

class AdminToken(BaseModel):
    access_token: str
    token_type: str
    admin_details: Optional[Dict[str, str]]

class UserUpdate(BaseModel):
    username: str
    name: str
    email: str
    contactnumber: int
    bankname: str | None = None
    branch: str | None = None
    acctype: str | None = None
    dob: str | None = None
    address: str | None = None


class MortgageDetails(BaseModel):
    username: str
    hasMortgage: bool
    mortgageCount: Optional[str] = None
    resOrBuyToLet: Optional[str] = None
    mortgageType: Optional[str] = None
    mortgageAmount: Optional[str] = None
    renewalDate: Optional[str] = None
    isLookingForMortgage: Optional[bool] = None
    newMortgageAmount: Optional[str] = None
    ownershipType: Optional[str] = None
    depositeAmt: Optional[str] = None
    annualIncome: Optional[str] = None
    foundProperty: Optional[str] = None

class UserMortgageDetails(BaseModel):
    id: str
    username: str
    name: str
    email: str
    contactnumber: int
    hasMortgage: bool
    mortgageCount: Optional[int] = None
    resOrBuyToLet: Optional[str] = None
    mortgageType: Optional[str] = None
    mortgageAmount: Optional[str] = None
    renewalDate: Optional[str] = None
    isLookingForMortgage: Optional[bool] = None
    newMortgageAmount: Optional[str] = None
    ownershipType: Optional[str] = None
    annualIncome: Optional[str] = None

    class Config:
        from_attributes = True



class ExistingMortgageDetail(BaseModel):
    id: str  # Serialized `_id` from MongoDB
    hasMortgage: bool
    mortgageCount: str
    resOrBuyToLet: str
    mortgageType: str
    mortgageAmount: str
    renewalDate: Optional[str]


class NewMortgageRequest(BaseModel):
    id: str  # Serialized `_id` from MongoDB
    isLookingForMortgage: bool
    newMortgageAmount: str
    ownershipType: str
    annualIncome: str
    depositeAmt: str
    foundProperty: str


class AllUser(BaseModel):
    id: str  # Serialized `_id` from MongoDB
    name: str
    username: str
    email: str
    contactnumber: int
    mortgage_details: Optional[List[ExistingMortgageDetail]]
    new_mortgage_requests: Optional[List[NewMortgageRequest]]