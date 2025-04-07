import os 

from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
from dotenv import load_dotenv

def get_client():
    load_dotenv()
    return Client(
    bearer_auth_credentials=BearerAuthCredentials(
        # access_token=os.environ['SQUARE_ACCESS_TOKEN']
        access_token=os.environ.get("SQUARE_TOKEN")
    ),
    environment='production')