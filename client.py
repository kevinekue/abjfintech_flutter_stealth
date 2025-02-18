from typing import Annotated

from fastapi import HTTPException
import httpx
import motor.motor_asyncio
from models import PaymentRequest, Transaction
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_db_url: str
    db_name: str
    collection_name: str
    flutter_sk: str
    transaction_initiation_url: str
    transaction_verification_url: str    
    model_config = SettingsConfigDict(env_file= ".env")

setting = Settings()

client = motor.motor_asyncio.AsyncIOMotorClient(setting.mongo_db_url)
db = client.get_database(setting.db_name)
transactions_collection = db.get_collection(setting.collection_name)

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


"""
Database Ops
"""


async def add_transaction_to_db(transaction_data: Transaction):
    '''
    Transaction data insertion
    '''
    if (
        transaction_db := await transactions_collection.find_one({"id": transaction_data.id})
    ) is None:        
        print('about to insert transaction')
        await transactions_collection.insert_one(transaction_data.model_dump(by_alias=True))
        print('just inserted transaction')
    else:
        await transactions_collection.find_one_and_update({"id": transaction_data.id}, {"$set":transaction_data.model_dump(by_alias=True)})


async def fetch_transaction_info(transaction_id: str):
    '''
    Transaction data update
    '''

    print('checking for transaction id')
    if (
        transaction_db := await transactions_collection.find_one({"id": transaction_id})     
    ) is not None:
        transaction_db.pop('_id', None)
        return transaction_db
    
    
    raise HTTPException(status_code=404, detail=f"ExceptionId {transaction_id} not found")

"""
FlutterWave API Ops
"""

def initiate_payment_client(payment_request: PaymentRequest):
    headers ={
        "Authorization": f"Bearer {setting.flutter_sk}",
        "Content-Type":"application/json"
    }

    client_response = httpx.post(setting.transaction_initiation_url, headers=headers, json=payment_request.to_dict())
    
    if(client_response.json().get("data") is None):
        raise HTTPException(status_code=client_response.status_code, detail=client_response.json().get("message"))
    
    payment_initiation_response = Transaction(**client_response.json().get("data"))
    payment_initiation_response.update_status(payment_initiation_response.status)

    return payment_initiation_response



async def verify_transaction_status_client(transaction_id : str):
    headers ={
        "Authorization": f"Bearer {setting.flutter_sk}",
        "Content-Type":"application/json"
    }
    transaction_url = f'{setting.transaction_verification_url}/{transaction_id}/verify'

    client_response = httpx.get(transaction_url, headers=headers)

    #  Exception if null data from flutterwave
    if(client_response.json().get("data") is None):
        raise HTTPException(status_code=client_response.status_code, detail=client_response.json().get("message"))
    
    #   Casting the data to a Transaction object
    client_response_cast = Transaction(**client_response.json().get("data"))
    
    # Checking if transaction_id exists in the db
    db_check_response = await fetch_transaction_info(client_response_cast.id)

    # if exists, we first generate a Transaction object, 
    # then we check if the latest status entry in the history matches what's received from the client
    # if different, we update the status history, and add the updated transaction to the db
    # then we return the up to date info from our db to the end user
    if(db_check_response is not None):
        db_check_response_cast = Transaction(**db_check_response)

    
        if(list(db_check_response_cast.status_history.values())[-1] != client_response_cast.status):
            client_response_cast.status_history = db_check_response_cast.status_history
            client_response_cast.update_status(client_response_cast.status)
            await add_transaction_to_db(client_response_cast)
            return client_response_cast

        return db_check_response_cast
    
    #   if the db for some reason doesn't have the transaction recorded, we proceed to save it here
    return await add_transaction_to_db(client_response_cast)
