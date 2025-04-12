from src.get_square_categories import get_category_dictionary
from src.get_client import get_client
from src.get_client import SquareAPIException

# my modules 
from src.square_dates import get_dates_from_date_file, get_open_close_time
from src.get_square_products import get_square_products

"""
CATEGORY FILE READING 
"""
def get_category_restock_keys(category_dict):
    restock_categories = []
    with open("restock_categories.txt", "r") as restock_categories_file:
        keys = [line.rstrip().replace(" ", "_").upper() for line in restock_categories_file]
        restock_categories = [category_dict[catkey] for catkey in keys]
    return restock_categories

def category_needs_restock(restock_categories, category_id):
    if category_id in restock_categories:
        return True
    return False

if __name__ == "__main__":

    try:
        # accessing the square API requires calling this function
        client = get_client()
    except SquareAPIException as e:
        print(e)
        print("Failure to connect to square, is your API Token correct?")
        exit(0)


    open_date, close_date = get_dates_from_date_file() 

    if not open_date or not close_date:
        exit(0) 


    # now ready for using for getting inventory changes 
    open_time, close_time = get_open_close_time(open_date, close_date)

    # gets all products that have had inventory changes between opening on open_time and closing on closing_time 
    products = get_square_products(client, open_time, close_time)

    category_dictionary = get_category_dictionary(client)
    restock_categories = get_category_restock_keys(category_dictionary)
    # [print(json.dumps(product.catalog_object, indent=4)) for product in products]
    # filtering out the items labeled as games 
    game_products = [product for product in products if category_needs_restock(restock_categories, product.get_category_id()) and product.is_to_sold()]

    inventory_strings = [str(game_product) for game_product in game_products]
    unique_inventory_strings = list(set(inventory_strings))
    unique_inventory_strings.sort()

    pretty_open_date = open_date.strftime("%Y-%m-%d")
    pretty_close_date = close_date.strftime("%Y-%m-%d")

    with open(f"prior_records/{pretty_open_date}{pretty_close_date}.csv", "w") as file:
        file.write("Category,Title,Variation,Floor,Backstock,Square,Notes,Done?\n")
        [file.write(f"{uis}\n") for uis in unique_inventory_strings]



    