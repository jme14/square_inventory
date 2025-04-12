from src.get_client import get_client
from src.get_square_products import get_catalog_objects_from_ids

def get_all_category_ids(client):
    category_ids = []
    cursor=None
    runs = 0
    while True:
        # Make a request to the Catalog API
        response = client.catalog.list_catalog(
            cursor=cursor,
            types='CATEGORY'
        )

        runs = runs+1
        if response.is_success():
            # Extract categories from the response
            categories = response.body.get('objects', [])
            for category in categories:
                if category['type'] == 'CATEGORY':
                    category_ids.append(category['id'])
            
            # Check if there's another page of results (pagination)
            cursor = response.body.get('cursor')
            if not cursor:
                break
        else:
            print(f"Error fetching categories: {response.errors}")
            break
    return category_ids

# the main of this module 
def get_category_dictionary(client):
    print("Getting category dictionary...")
    category_dict = {}

    category_ids = get_all_category_ids(client)
    category_catalog_objects  = get_catalog_objects_from_ids(client, category_ids)
    both = zip(category_ids, category_catalog_objects)
    for category_id, category_catalog_object in both:
        uf_name = category_catalog_object["category_data"]["name"]
        name = uf_name.upper().replace(" ", "_")
        category_dict[name] = category_id
    return category_dict

if __name__ == "__main__":
    client = get_client()
    cat_dict = get_category_dictionary(client)
    print(cat_dict)