from enum import Enum

from pydantic import BaseModel


class OperationType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOut(BaseModel):
    uuid: str
    balance: int


class WalletUpdate(BaseModel):
    amount: int
    operation_type: OperationType
