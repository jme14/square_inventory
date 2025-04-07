from src.get_client import get_client 
from src.get_client import SquareAPIException
from src.get_square_categories import get_all_category_ids, get_category_dictionary

def test_get_client_with_env():
    try:
        get_client()
    except SquareAPIException as e:
        print(e)

def test_square_categories():
    client = get_client()
    all_ids = get_all_category_ids(client)
    assert len(all_ids) > 0
    id_dict = get_category_dictionary(client)
    assert len(all_ids) == len(id_dict)