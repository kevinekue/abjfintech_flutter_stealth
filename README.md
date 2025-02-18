# abjfintech_flutterwave_api
### Flutterwave_Stealth: API Integration exercise with FastAPI and MongoDB

This project was built with the intention to demo a Plutterwave api integration.
It assumes that the reader has Python installed (https://www.python.org/downloads/), and ideally a virtual environment set up (https://docs.python.org/3/library/venv.html) 

It exclusively focuses here on the following two functionalities:
* A payment transaction initiation within francophone Africa: ```/payment/initiate```
* A status verification of said transaction: ``` /payment/verify?transaction_id={transaction_id_value}```

In order to run this api locally, you'll need the following: 
* A Flutterwave test account: it's required for the retrieval of your api keys (https://flutterwave.com/tz/support/my-account/getting-your-api-keys), and api whitelisting(https://flutterwave.com/ng/support/integrations/how-to-whitelist-ip-addresses-on-your-flutterwave-dashboard)
* Your Mongo Database instance's connection details.
* Python installed on your local instance. The additional libraries required can be found in the `requirements.txt` file
* Update the `.env` file with the information pertaining to your specific project

to run the api:

```bash
# Navigate to the directory
# Upgrade pip
pip install --upgrade pip

# Install the requirements:
pip install -r requirements.txt

# Start the service:
uvicorn main:app --reload

# Stop the service
CTRL + C

# To run the unit tests, simply enter the following in your terminal
pytest
```

You can access an interactive API documentation that will allow you to place sample requests once the api's running:
* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc
* You can also import the swagger spec (found in ```flutterwave_stealth/swagger.json```) in postman to generate a collection and test the api. 