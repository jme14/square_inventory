from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
from datetime import datetime, timedelta
import os
import json

import requests

GAMES="PEDVXQTFWX7G3RRW234W4X3A"
ROLE_PLAYING_GAMES="VESLZYNK6DWJEFYQI3VI7DXK"
DICE="VRIPWLSL2TKXZODDA2DDETEU"
PUZZLES="RB6VYRDFJGYX3IBUO45BVBG5"
GAMING_ACCESSORIES="HWQCO5EPF7BTFFZ37G3OTYQT"
MAGIC_THE_GATHERING="GXR4JX6T7NK46PPYRPDNTWIR"
MINIATURES_AND_MINIS_SYSTEMS="SCOOKY7NXKKI3RHBANORZOVL"
POKEMON_TCG="TQQOIPFQEAP7B2JPFE5E55VP"
CAFÉ_DRINKS="PHSJ75IXSQXRFFFFHYACF2RZ"
EVENTS="WX7WOX2G4BQITYCVOTQ4MK5O"
COLLECTIBLE_CARD_GAMES="6MMNL6N7EOQAUCL2G6SC5DVG"
LIVING_CARD_GAMES="FWWG3AFAQ6SROH4Q4G6UEZCS"
SANDWICHES="XPMITEVRWOCBIP46P63M2CKE"
BAR_DRINKS="SECK7XGHAN6VQ3546FWSJCKA"
BOTTLED_ALCOHOL="TGS6DM5SAYOILURCG23VZWWK"
DRAFT_BEER_OR_CIDER="IHW7OWGZMFMFEIL2IZQQEMOL"
MEMBERSHIP="R6YZHB2Z3QPGTIJ2ULRQV3ZY"
WARGAMING="6KCDOOCNODYZ7Z7Q4YGP5HAP"
MERCH="ILOVTBNVQNEO4LNSJH33HGJN"
LORCANA="PTGOQ2THYORJF4LWDHTMT6CM"
GAME_PASS="QI6UVNBDTVBRBWGNYZSUGRJE"
POP_UP="VRYBKMQDEULGHOHAOQYHITEL"
SHAREABLES="4RZQYJABRHVKQ2QDO3RITLC4"
SIDES="4FNIMGSJOO7HLWQX5CHHWR77"
SPOOKEASY="IOIVVBUYAEAE4XXJW5VRIQCR"
WINTER_WONDERLAND="ZVAXHPK7WWASGKYFG43LWMP6"
BOTTLED_NON_ALCOHOLIC="QLU7YKXIGEXUB7TJ57IGVAGV"
SCHOOL_SPECIALS="PEAXJ62E37P6PQXR3STWL3AY"
LEGOS="3MT4C7XNIQR2UUNJHFAG3JMX"
YOUTH_PROGRAMMING="JH7576HVYVBDJOEVDG5QQCZJ"
GRAB_AND_GO="S46JPFKM6TLPLQSHSDO27EHB"
MIDWEST_PARADISE="TZ2EOASB2MWPQLJTEVREMOS7"
CLASSICS_KIDS="5BWHDTREMYUWBBQ6QQBCCJZI"
BEST_SELLERS="OQEHF5KPP437ZEJJUGXOI2KQ"
GATEWAY_GAMES="V77CTMNEZXZJZ2V6TAIXEK2V"
TWO_PLAYER="NIEK67P4YZZRHGK5OWP22XPM"
UPCOMING_EVENTS="BLOWEEZJ5WISQGSVRLQEJCPM"

def category_needs_restock(category_id):
    needs_restock = [
        GAMES,
        ROLE_PLAYING_GAMES,
        DICE,
        PUZZLES,
        GAMING_ACCESSORIES,
        MINIATURES_AND_MINIS_SYSTEMS,
        POKEMON_TCG,
        LIVING_CARD_GAMES,
        GRAB_AND_GO,
        BOTTLED_ALCOHOL,
        BOTTLED_NON_ALCOHOLIC
    ]
    if category_id in needs_restock:
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
            return "" 
    
    # true on adjustment was from something to sold 
    def is_to_sold(self):
        return self.inventory_adjustment["adjustment"]["to_state"] == "SOLD"




def get_client():
    return Client(
    bearer_auth_credentials=BearerAuthCredentials(
        access_token=os.environ['SQUARE_ACCESS_TOKEN']
    ),
    environment='production')

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
        print("An error occurred")
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
        [all_results.append(change) for change in result.body["changes"]]

    return all_results
def get_catalog_objects_from_ids(client, catalog_object_id_array):

    for coi in catalog_object_id_array:
        
        if not isinstance(coi, str):
            print("THIS ONE:")
            print(coi)

    catalog_objects_returned = client.catalog.batch_retrieve_catalog_objects(
        body = {
            "object_ids": catalog_object_id_array
        }
    )

    if catalog_objects_returned.is_error():
        print("An error occurred")
        for error in catalog_objects_returned.errors:
            print(error['category'])
            print(error['code'])
            print(error['detail'])
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
    if not result.is_success():
        return []
    
    return [inventory_count for inventory_count in result.body["counts"]] 

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
            if inventory_count["catalog_object_id"] == square_product.catalog_object_id:
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
                square_product.category_object = get_catalog_objects_from_ids(client, [category_id])[0]
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

    # accessing the square API requires calling this function
    client = get_client()

    open_date, close_date = get_dates_from_date_file() 

    if not open_date or not close_date:
        exit(0) 


    # now ready for using for getting inventory changes 
    open_time, close_time = get_open_close_time(open_date, close_date)

    # gets all products that have had inventory changes between opening on open_time and closing on closing_time 
    products = get_square_products(client, open_time, close_time)

    # filtering out the items labeled as games 
    game_products = [product for product in products if category_needs_restock(product.get_category_id()) and product.is_to_sold()]

    inventory_strings = [str(game_product) for game_product in game_products]
    unique_inventory_strings = list(set(inventory_strings))
    unique_inventory_strings.sort()

    pretty_open_date = open_date.strftime("%Y-%m-%d")
    pretty_close_date = close_date.strftime("%Y-%m-%d")

    with open(f"prior_records/{pretty_open_date}{pretty_close_date}.csv", "w") as file:
        file.write("Category,Title,Variation,Floor,Backstock,Square,Notes,Done?\n")
        [file.write(f"{uis}\n") for uis in unique_inventory_strings]



    