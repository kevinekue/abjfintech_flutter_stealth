import threading
from typing import List

from client import add_transaction_to_db, initiate_payment_client, verify_transaction_status_client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import (PaymentRequest, Transaction)

app = FastAPI()

origins = [
    "http://localhost:8000",  # Replace with your frontend's origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"Hello":"Abj Fintech x Flutter"}

def serialize_object(obj):
    return {k: v for k, v in obj.__dict__.items() if not isinstance(v, threading.Lock)}


@app.post("/api/v1/payment/initiate", response_model_by_alias=False, response_model=Transaction)
async def initiate_payment(payment_info: PaymentRequest):

    payment_initiation_response = initiate_payment_client(payment_info)
    await add_transaction_to_db(payment_initiation_response)
    return payment_initiation_response

@app.get("/api/v1/payment/verify", response_model_by_alias=False, response_model=Transaction)
async def verify_transaction(transaction_id: str):

    return await verify_transaction_status_client(transaction_id)
