from datetime import datetime, timedelta
import json
from src.get_square_categories import get_category_dictionary
from src.get_client import get_client
from src.get_client import SquareAPIException


def category_needs_restock(category_dict, category_id):

    restock_categories = []
    with open("restock_categories.txt", "r") as restock_categories_file:
        keys = [line.rstrip().replace(" ", "_").upper() for line in restock_categories_file]
        restock_categories = [category_dict[catkey] for catkey in keys]

    if category_id in restock_categories:
        return True
    return False

class SquareProduct:
    def __init__(self, catalog_object_id, inventory_adjustment):
        self.catalog_object_id = catalog_object_id
        self.inventory_adjustment = inventory_adjustment
        self.category_object = {}
        self.catalog_object = {} 
        self.parent_catalog_object = {}
        self.inventory_count = {}
    
    def __str__(self):
        try:
            item_name = self.parent_catalog_object["item_data"]["name"]
            item_variation = self.catalog_object["item_variation_data"]["name"] 
            inventory_quantity = self.inventory_count["quantity"]
            category_name = self.get_category_name()
            return f"\"{category_name}\",\"{item_name}\",\"{item_variation}\",,,{inventory_quantity},"
        except KeyError:
            return f""

    def get_detailed_string(self):
        if not self.catalog_object: 
            return f"ID: {self.catalog_object_id}\nADJUSTMENT: {json.dumps(self.inventory_adjustment, indent=3)}\n(No Catalog Object)"
        if not self.parent_catalog_object: 
            return f"ID: {self.catalog_object_id}\nADJUSTMENT: {json.dumps(self.inventory_adjustment, indent=3)}\nCATALOG OBJECT: {json.dumps(self.catalog_object, indent=3)}\n(No Parent Catalog Object)"
        if not self.inventory_count: 
            return f"ID: {self.catalog_object_id}\nADJUSTMENT: {json.dumps(self.inventory_adjustment, indent=3)}\nCATALOG OBJECT: {json.dumps(self.catalog_object, indent=3)}\nPARENT CATALOG OBJECT: {json.dumps(self.parent_catalog_object, indent=3)}\n(No Inventory Count)"
        return f"ID: {self.catalog_object_id}\nADJUSTMENT: {json.dumps(self.inventory_adjustment, indent=3)}\nCATALOG OBJECT: {json.dumps(self.catalog_object, indent=3)}\nPARENT CATALOG OBJECT: {json.dumps(self.parent_catalog_object, indent=3)}\nINVENTORY COUNT: {json.dumps(self.inventory_count, indent=3)}\n"

    # example, from IN STOCK to SOLD OUT 
    def get_from_state_to_state_string(self):
        from_state = self.inventory_adjustment["adjustment"]["from_state"]
        to_state = self.inventory_adjustment["adjustment"]["to_state"]
        return f"{from_state} -> {to_state}"

    def get_inventory_change_string(self):
        item_name = self.parent_catalog_object["item_data"]["name"]
        item_variation = self.catalog_object["item_variation_data"]["name"] 
        inventory_quantity = self.inventory_count["quantity"] 
        return f"{self}\n{self.get_from_state_to_state_string()}\n"

    # BELOW IS HOW ATTRIBUTES WE CARE ABOUT ARE OBTAINED 
    # we should never directly access the dictionary 
    def get_category_id(self):
        parent_catalog_obj = self.parent_catalog_object
        if parent_catalog_obj == {}:
            return ""
        if "reporting_category" not in parent_catalog_obj["item_data"]:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("WARNING: THE FOLLOWING DOESN'T HAVE A REPORTING CATEGORY")
            print(self)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            return ""
        return parent_catalog_obj["item_data"]["reporting_category"]["id"]

    def get_category_name(self):
        category_object = self.category_object
        try:
            return category_object["category_data"]["name"]
        except KeyError:
            return "ERROR"

    def get_item_id(self):
        try:
            return self.catalog_object["item_variation_data"]["item_id"]
        except KeyError:
            print("ERROR WITH THIS ITEM...was it deleted?")
            print(self.get_detailed_string())
            return "" 
    
    # true on adjustment was from something to sold 
    def is_to_sold(self):
        return self.inventory_adjustment["adjustment"]["to_state"] == "SOLD"


def get_square_time(year, month, date, hour, minute):
    return (datetime(year, month, date, hour, minute, 0, 0)+timedelta(hours=7))

def get_open_close_time(open_datetime, close_datetime):
    return (open_datetime+timedelta(hours=7)+timedelta(hours=8), close_datetime+timedelta(hours=7)+timedelta(hours=26))

def get_inventory_changes(client, open_time, close_time):
    result = client.inventory.batch_retrieve_inventory_changes(
        body = {
            "types": [
                "ADJUSTMENT"
            ],
            "updated_after": open_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_before":  close_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    )

    if result.is_error():
        print("An error occurred getting inventory items...")
        print(json.dumps(result, indent=4))
        exit

    all_results = []
    if not result.is_success:
        return all_results 
    if not result.cursor:
        [all_results.append(change) for change in result.body["changes"]]
        return all_results

    [all_results.append(change) for change in result.body["changes"]]
    while result.cursor:
        result = client.inventory.batch_retrieve_inventory_changes(
            body = {
                "types": [
                    "ADJUSTMENT"
                ],
                "updated_after": open_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated_before":  close_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "cursor": result.cursor
            }
        )
        if (result.body == {}):
            break
        [all_results.append(change) for change in result.body["changes"] if result.body["changes"]]

    return all_results
def get_catalog_objects_from_ids(client, catalog_object_id_array):

    for coi in catalog_object_id_array:
        
        if not isinstance(coi, str):
            print("THIS ONE:")
            print(coi)
    # attempting to fix the too many items error
    if len(catalog_object_id_array) > 1000:
        coi_chunks = []
        for i in range(0, len(catalog_object_id_array), 1000):
            coi_chunks.append(catalog_object_id_array[i:i+1000])
        print(f"Many objects...splitting into {len(coi_chunks)} sections")
        all_objects = []
        #print(coi_chunks)
        for chunk in coi_chunks:
            all_objects.append(get_catalog_objects_from_ids(client, chunk))
        return [item for sublist in all_objects for item in sublist]


    catalog_objects_returned = client.catalog.batch_retrieve_catalog_objects(
        body = {
            "object_ids": catalog_object_id_array
        }
    )

    if catalog_objects_returned.is_error():
        print("An error occurred")
        for error in catalog_objects_returned.errors:
            print(json.dumps(error, indent=4))
            # print(error['category'])
            # print(error['code'])
            # print(error['detail'])
        exit

    if not catalog_objects_returned.is_success:
        return []

    return [catalog_object for catalog_object in catalog_objects_returned.body.get("objects", [])] 

def get_inventory_counts(client, catalog_object_id_array):
    result = client.inventory.batch_retrieve_inventory_counts(
        body = {
            "catalog_object_ids": catalog_object_id_array
        }
    )
    # attempting to fix the too many items error
    if len(catalog_object_id_array) > 1000:
        coi_chunks = []
        for i in range(0, len(catalog_object_id_array), 1000):
            coi_chunks.append(catalog_object_id_array[i:i+1000])
        print(f"Many objects...splitting into {len(coi_chunks)} sections")
        all_objects = []
        #print(coi_chunks)
        for chunk in coi_chunks:
            all_objects.append(get_inventory_counts(client, chunk))
        return [item for sublist in all_objects for item in sublist]
    if not result.is_success():
        print("An error occurred getting the inventory counts")
        print(result)
        return []
    
    return [inventory_count for inventory_count in result.body["counts"]] 
def get_category_object_from_id(client, category_object_id):
    if category_object_id == "":
        return "No Category"
    return get_catalog_objects_from_ids(client, [category_object_id])[0]
    

def get_square_products(client, open_time, close_time):
    print("Getting inventory changes...")
    # only getting the square products that have been purchased within this timeframe  
    inventory_changes = get_inventory_changes(client, open_time, close_time) 

    # only care about if an adjustment happens, not other types of changes 
    inventory_adjustments = [adjustment for adjustment in inventory_changes if adjustment["type"] == "ADJUSTMENT"] 

    # getting the catalog_object_array from the inventory adjustments 
    coi_array = [catalog_object_id["adjustment"]["catalog_object_id"] for catalog_object_id in inventory_adjustments]

    # creation of square product objects  
    square_products = [SquareProduct(coi, adj) for coi,adj in zip(coi_array, inventory_adjustments)]

    print("Getting catalog objects...")
    # get the actual catalog objects given the catalog object array 
    catalog_objects = get_catalog_objects_from_ids(client, coi_array)

    # match catalog objects with square object records 
    # this is because there are fewer catalog objects than square products due to products being bought twice 
    for catalog_object in catalog_objects:
        for square_product in square_products:
            if catalog_object["id"] == square_product.catalog_object_id:
                square_product.catalog_object = catalog_object
    
    # getting the catalog object ids for parent objects here 
    parent_coi_array = [square_product.get_item_id() for square_product in square_products if square_product.get_item_id() != ""]
    #parent_coi_array = []
    #for square_product in square_products:
        #try:
            #parent_coi_array.append(square_product.catalog_object["item_variation_data"]["item_id"])
        #except KeyError:
            #print(square_product)


    print("Getting parent catalog objects...")
    # doing the same thing, except instead of for item variations doing it for items (or children to parent)
    parent_catalog_objects = get_catalog_objects_from_ids(client, parent_coi_array)

    # match parent catalog objects with square object records 
    for parent_catalog_object in parent_catalog_objects:
        for square_product in square_products:
            if parent_catalog_object["id"] == square_product.get_item_id():
                square_product.parent_catalog_object = parent_catalog_object
            
    print("Getting inventory counts...")
    # getting the inventory counts given the catalog object arrays 
    inventory_counts = get_inventory_counts(client, coi_array)

    # match inventory counts with square object records 
    for inventory_count in inventory_counts :
        for square_product in square_products:
            if (inventory_count["catalog_object_id"] == square_product.catalog_object_id) and (inventory_count["state"] != "RETURNED_BY_CUSTOMER"):
                square_product.inventory_count = inventory_count 


    print("Getting category objects...")
    
    # this will be a set of all the category ids of this run
    processed_categories = {}
    # for all square products... 
    for square_product in square_products:
        # get the category id...
        category_id = square_product.get_category_id()
        # if it hasn't been processed, look for it 
        if category_id not in processed_categories.keys():
            try:
                #square_product.category_object = get_catalog_objects_from_ids(client, [category_id])[0]
                square_product.category_object = get_category_object_from_id(client, category_id)
                processed_categories[category_id] = square_product.category_object
            except IndexError:
                square_product.category_object = {}
        # otherwise, just get it 
        else:
            square_product.category_object = processed_categories[category_id]
    return square_products

def get_dates_from_date_file():
    with open("dates.txt", "r") as file:
        open_date_string = file.readline().strip()
        close_date_string = file.readline().strip()
        try:
            open_date = datetime.strptime(open_date_string, "%Y-%m-%d")
            close_date = datetime.strptime(close_date_string, "%Y-%m-%d")
            return open_date, close_date
        except ValueError as e:
            print("ERROR: format the dates in YYYY-MM-DD format in each row")
            return None, None

if __name__ == "__main__":

    try:
        # accessing the square API requires calling this function
        client = get_client()
    except SquareAPIException as e:
        print(e)
        print("Failure to connect to square, is your API Token correct?")
        exit(0)

    category_dictionary = get_category_dictionary(client)

    open_date, close_date = get_dates_from_date_file() 

    if not open_date or not close_date:
        exit(0) 


    # now ready for using for getting inventory changes 
    open_time, close_time = get_open_close_time(open_date, close_date)

    # gets all products that have had inventory changes between opening on open_time and closing on closing_time 
    products = get_square_products(client, open_time, close_time)

    # [print(json.dumps(product.catalog_object, indent=4)) for product in products]
    # filtering out the items labeled as games 
    game_products = [product for product in products if category_needs_restock(category_dictionary, product.get_category_id()) and product.is_to_sold()]

    inventory_strings = [str(game_product) for game_product in game_products]
    unique_inventory_strings = list(set(inventory_strings))
    unique_inventory_strings.sort()

    pretty_open_date = open_date.strftime("%Y-%m-%d")
    pretty_close_date = close_date.strftime("%Y-%m-%d")

    with open(f"prior_records/{pretty_open_date}{pretty_close_date}.csv", "w") as file:
        file.write("Category,Title,Variation,Floor,Backstock,Square,Notes,Done?\n")
        [file.write(f"{uis}\n") for uis in unique_inventory_strings]



    