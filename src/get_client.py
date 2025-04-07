import os 

from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
from dotenv import load_dotenv

class SquareAPIException(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(message)

    def __str__(self):
        return f"{self.message} - {self.errors if self.errors else 'No additional error info'}"

# returns client on success and throws exception on failure 
def get_client():
    load_dotenv()
    access_token = os.environ.get("SQUARE_TOKEN")
    client = Client(
    bearer_auth_credentials=BearerAuthCredentials(
        access_token=access_token
    ),
    environment='production')

    # can we get the location?
    locations_api = client.locations
    response = locations_api.list_locations()

    # if not, throw exception
    if response.is_error():
        raise SquareAPIException("Failure to connect to Square API", response.errors)
        
    return client