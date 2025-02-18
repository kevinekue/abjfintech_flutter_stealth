import datetime
from enum import Enum
from json import JSONEncoder
from pydantic import BaseModel, BeforeValidator, ConfigDict
from typing import Annotated, Optional


PyObjectId = Annotated[str, BeforeValidator(str)]

class Currency(str, Enum):
    ngn = "NGN"
    gh = "GHS"
    kes = "KES"
    ugx = "UGX"
    tzx = "TZS"
    usd = "USD"
    ot = "OT"
    xof = "XOF"
    xaf = "XAF"

class PaymentRequest(BaseModel):
    phone_number: str
    amount: float # N.B. Amount should not be less than 100.
    currency: Currency
    email: Optional [str] = None
    tx_ref: str
    is_mobile_money_franco:Optional [bool] = None 
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "phone_number": "24709929220",
                "amount": 100,
                "currency": "XAF",
                "email": "JoeBloggs@acme.co",
                "tx_ref": "gvghbv"
            }
        },
    )

    def to_dict(self):
        return self.__dict__

class Customer(BaseModel):
    id: int
    phone_number: str
    name: str
    email: str
    created_at: str

    def to_dict(self):
        return self.__dict__

class Transaction(BaseModel):
    id: int
    tx_ref: Optional [str] = None
    flw_ref: Optional [str] = None
    device_fingerprint: Optional [str] = None
    amount: Optional [float] = None
    amount_settled: Optional[float] = None
    charged_amount: Optional [float] = None
    app_fee: Optional [float] = None
    merchant_fee: Optional [float] = None
    processor_response: Optional [str] = None
    auth_model: Optional [str] = None
    currency: Currency
    ip: Optional [str] = None
    narration: Optional [str] = None
    status: Optional [str] = None
    payment_type: Optional [str] = None
    fraud_status: Optional [str] = None
    charge_type: Optional [str] = None
    created_at: Optional [str] = None 
    account_id: int
    customer: Customer
    meta: Optional[str] = None  
    status_history: Optional[dict] = {}
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {"id": 8392688,
                    "tx_ref": "gvghbv",
                    "flw_ref": "FLWTK43726MCK1739776592306",
                    "device_fingerprint": "N/A",
                    "amount": 100,
                    "amount_settled": None,
                    "charged_amount": 100,
                    "app_fee": 2,
                    "merchant_fee": 0,
                    "processor_response": "Transaction in progress",
                    "auth_model": "AUTH",
                    "currency": "XAF",
                    "ip": "52.209.154.143",
                    "narration": "Keveen Roz 1739324087845",
                    "status": "pending",
                    "payment_type": "mobilemoneysn",
                    "fraud_status": "ok",
                    "charge_type": "normal",
                    "created_at": "2025-02-17T07:16:31.000Z",
                    "account_id": 2586597,
                    "customer": {
                    "id": 2589027,
                    "phone_number": "24709929220",
                    "name": "Anonymous customer",
                    "email": "JoeBloggs@acme.co",
                    "created_at": "2025-02-16T06:40:25.000Z"
                    },
                    "meta": None,
                    "status_history": {
                    "2025-02-17T01:16:32.678453": "pending"
                    }
                }
                },
    )


    def to_dict(self):
        return self.__dict__
    
    def update_status(self, status):
        timestamp = datetime.datetime.now().isoformat()
        self.status_history[str(timestamp)] = status
        # print(self.status_history)

    def get_status_history(self):
        return self.status_history

class PayloadEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
