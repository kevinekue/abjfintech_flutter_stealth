import httpx
import pytest
import json
import os
from fastapi.testclient import TestClient
from httpx import AsyncClient
import respx
from main import app  

client = TestClient(app)

def mock_data():
    init_request_file_path = os.path.join('./tests_resources_folder/initiation_request.json')
    with open(init_request_file_path, 'r', encoding='utf-8') as json_file:
        init_request = json.load(json_file)

    init_response_file_path = os.path.join('./tests_resources_folder/initiation_response.json')
    with open(init_response_file_path, 'r', encoding='utf-8') as json_file:
        init_response = json.load(json_file)
    
    verification_response_file_path = os.path.join('./tests_resources_folder/transaction_verification_response.json')
    with open(verification_response_file_path, 'r', encoding='utf-8') as json_file:
        verification_response = json.load(json_file)
    
    bad_currency_response_path = os.path.join('./tests_resources_folder/bad_currency_response.json')
    with open(bad_currency_response_path, 'r', encoding='utf-8') as json_file:
        bad_currency_response = json.load(json_file)

    missing_req_field_path = os.path.join('./tests_resources_folder/missing_req_field_response.json')
    with open(missing_req_field_path, 'r', encoding='utf-8') as json_file:
        missing_req_field_response = json.load(json_file)
    
    return {
            'init_request': init_request, 
            'init_response': init_response, 
            'bad_currency_response': bad_currency_response,
            'missing_req_field_response': missing_req_field_response,
            'verification_response': verification_response
            }

# Use AsyncClient for asynchronous tests
@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "Abj Fintech x Flutter"}

@pytest.mark.asyncio
@respx.mock
async def test_initiate_payment(async_client):
    mock_data_dict = mock_data()
    init_request = mock_data_dict['init_request']
    init_response = mock_data_dict['init_response']

    respx.post("/payment/initiate").mock(return_value=httpx.Response(200, json=init_response))

    response = await async_client.post("/payment/initiate", json=init_request)
    assert response.status_code == 200
    assert len(response.json()["status_history"]) == 1
    assert response.json()["status"] == "pending"
    assert response.json()["amount_settled"] is None

@pytest.mark.asyncio
@respx.mock
async def test_verify_transaction(async_client):
    mock_data_dict = mock_data()
    init_response = mock_data_dict['init_response']
    transaction_id = init_response["id"]

    transaction_verification_response = mock_data_dict['verification_response']
        
    respx.get(f"/payment/verify?transaction_id={transaction_id}").mock(return_value=httpx.Response(200, json=transaction_verification_response))

    response = await async_client.get(f"/payment/verify?transaction_id={transaction_id}")
    assert response.status_code == 200
    assert len(response.json()["status_history"]) == 2
    assert response.json()["status"] != init_response["status"]
    assert response.json()["status"] == "successful"
    assert response.json()["amount_settled"] is not None



@pytest.mark.asyncio
@respx.mock
async def test_initiate_payment_invalid_currency(async_client):
    mock_data_dict = mock_data()
    init_request = mock_data_dict['init_request']
    init_request['currency'] = 'randomCurrency'

    init_response_bad_currency = mock_data_dict['bad_currency_response']
        
    respx.post("/payment/initiate").mock(return_value=httpx.Response(422, json=init_response_bad_currency))

    response = await async_client.post("/payment/initiate", json=init_request)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be 'NGN', 'GHS', 'KES', 'UGX', 'TZS', 'USD', 'OT', 'XOF' or 'XAF'"



@pytest.mark.asyncio
@respx.mock
async def test_initiate_payment_missing_required_field(async_client):
    mock_data_dict = mock_data()
    init_request = mock_data_dict['init_request']
    init_request['tx_ref'] = None
    missing_req_field_response = mock_data_dict['missing_req_field_response']

    respx.post("/payment/initiate").mock(return_value=httpx.Response(422, json=missing_req_field_response))

    response = await async_client.post("/payment/initiate", json=init_request)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.json()["detail"][0]["loc"] == ["body", "tx_ref"]
