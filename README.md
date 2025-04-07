This is a script that allows for dynamically creating a csv based on items from a square library.

## Usage 
1) Put square access token in .env: `SQUARE_TOKEN="{token here}"`

2) Fill the restock_categories.txt file with the names of categories you wish to keep track of 
+ Make sure the names are correct, upon changing a category name the file will need editing 

3) Edit dates.txt to define the date range
+ Format YYYY-MM-DD
+ Both dates are inclusive

4) run `python -m src.main` to run, or `pytest` to test 

5) in the prior_records directory, find your spreadsheet! 
