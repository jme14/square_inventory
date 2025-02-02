from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
from datetime import datetime, timedelta
import os
import json


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

BOTTLE_RESTOCK_ATTRIBUTE_ID = "00bda8e9-974c-4d3c-83f4-1a30264a3f30"
def get_client():
    return Client(
    bearer_auth_credentials=BearerAuthCredentials(
        access_token=os.environ['SQUARE_ACCESS_TOKEN']
    ),
    environment='production')

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

def get_category_object_from_id(client, category_object_id):
    if category_object_id == "":
        return "No Category"
    return get_catalog_objects_from_ids(client, [category_object_id])[0]

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

class ZacProduct:
    def __init__(self, catalog_object_id):
        self.catalog_object_id = catalog_object_id
        self.catalog_object = {} 
        self.parent_catalog_object = {}
        self.inventory_count = {}
    def __str__(self):
        try:
            item_name = self.parent_catalog_object["item_data"]["name"]
            item_variation = self.catalog_object["item_variation_data"]["name"] 
            inventory_quantity = self.inventory_count["quantity"]
            system_price = self.get_price()
            return f"{item_name},{item_variation},{inventory_quantity},{system_price}"
        except KeyError:
            return f""

    def get_item_id(self):
        try:
            return self.catalog_object["item_variation_data"]["item_id"]
        except KeyError:
            print("WARNING: KEY ERROR!")
            return "" 
    def get_price(self):
        try:
            return float(self.catalog_object["item_variation_data"]["price_money"]["amount"])/100
        except KeyError:
            return -1 


def get_zac_objects():
    client = get_client()
    result = client.catalog.search_catalog_items(
        body = {
            "custom_attribute_filters": [{
                "key": BOTTLE_RESTOCK_ATTRIBUTE_ID,
                "bool_filter": True

            }]
        }
    )

    if result.is_error():
        print("An error occurred getting inventory items...")
        print(result)
        exit
    all_results = []

    if not result.is_success:
        return all_results 
    if not result.cursor:
        [all_results.append(item) for item in result.body["items"]]

    [all_results.append(item) for item in result.body["items"]]
    while result.cursor:
        result = client.catalog.search_catalog_items(
            body = {
                "custom_attribute_filters": [{
                    "key": BOTTLE_RESTOCK_ATTRIBUTE_ID,
                    "bool_filter": True
                }]
            }
        )
        try:
            [all_results.append(item) for item in result.body["items"]]
        except KeyError:
            print("No more!")

    # at this point, all results is all items with the bottle restock value of YES
    all_ids = []
    for item in all_results:
        # print(json.dumps(item, indent=4))
        # exit(0)
        try:
            print(json.dumps(item["item_data"]["variations"]))
            for variation in item["item_data"]["variations"]:
                all_ids.append(variation["id"])
        except KeyError:
            print("No variations")
            print(json.dumps(item, indent=4))
    
    zac_items = [ZacProduct(coi) for coi in all_ids]
    zac_items_coi_array = [zac_item.catalog_object_id for zac_item in zac_items]
    inventory_counts = get_inventory_counts(client, zac_items_coi_array)
    for count in inventory_counts:
        for zac_item in zac_items:
            if zac_item.catalog_object_id == count["catalog_object_id"]:
                zac_item.inventory_count = count
    
    # all that remains is getting catalog objects 
    catalog_object_array = get_catalog_objects_from_ids(client, zac_items_coi_array)
    for co in catalog_object_array:
        for zac_item in zac_items:
            if zac_item.catalog_object_id == co["id"]:
                zac_item.catalog_object = co
    
    parent_coi_array = [zac_item.get_item_id() for zac_item in zac_items] 
    parent_catalog_object_array = get_catalog_objects_from_ids(client, parent_coi_array)
    for pco in parent_catalog_object_array:
        for zac_item in zac_items:
            if zac_item.get_item_id() == pco["id"]:
                zac_item.parent_catalog_object = pco

    return zac_items



if __name__ == "__main__":
    all_items = get_zac_objects()
    [print(item) for item in all_items]
    exit(0)