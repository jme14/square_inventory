from get_client import get_client

def get_all_category_ids():
    client = get_client()

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

def write_category_info(category_ids):
    client = get_client()
    with open("category_info.txt", "w") as file:
        for category_id in category_ids:
            result = client.catalog.retrieve_catalog_object(object_id=category_id)
            # print(json.dumps(result.body, indent=4))
            name = result.body["object"]["category_data"]["name"]
            file.write(f"{name.upper().replace(" ", "_")}=\"{category_id}\"\n")

def get_category_dictionary(client):
    print("Getting category dictionary...")
    category_dict = {}

    category_ids = get_all_category_ids()
    client = get_client()
    for category_id in category_ids:
        result = client.catalog.retrieve_catalog_object(object_id=category_id)
        # unformatted name 
        uf_name = result.body["object"]["category_data"]["name"]
        name = uf_name.upper().replace(" ", "_")
        category_dict[name] = category_id
    return category_dict

def write_category_ids_file():
    category_ids = get_all_category_ids()
    write_category_info(category_ids)
    with open("category_ids.txt", "w") as file:
        [file.write(f"{id}\n") for id in category_ids]

    
if __name__ == "__main__":
    client = get_client()
    cat_dict = get_category_dictionary(client)
    print(cat_dict)