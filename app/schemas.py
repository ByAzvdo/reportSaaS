from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CoolingCheckCreate(BaseModel):
    time: Optional[str]
    temperature: Optional[str]
    personnel: Optional[str]
    corrective_action: Optional[str]
    verification_signature: Optional[str]

class CoolingCheckOut(CoolingCheckCreate):
    id: int

class ReportCreate(BaseModel):
    fried_item: Optional[str]
    lot_number: Optional[str]
    date: Optional[date]
    start_time: Optional[str]
    end_time: Optional[str]
    total_fried: Optional[int]
    goal: Optional[int]
    oil_lot: Optional[str]
    comments: Optional[str]
    team: Optional[str]
    leader_signature: Optional[str]
    cooling_checks: List[CoolingCheckCreate] = []

class ReportOut(ReportCreate):
    id: int
    cooling_checks: List[CoolingCheckOut] = []
