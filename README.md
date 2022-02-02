# QB-invoice-creator

## Description
Welcome to the Quickbooks invoice creator! This was written specifically for sending out SigEp NJA's semesterly dues, but it could be applied to any QB invoice with a few modifications. Currently, it expects that you have a csv with the emails of invoicees, their payment methods, and their status as a 'resident.' Being a resident means that the invoicee will pay a different amount than a non resident. You must have already created items in QB that have the amounts associated with them. Credentials.json asks for two sets of credentials, production and sandbox. The sandbox credentials are meaningless to the script as is, but if in script.py you change every instance of "prod" to "sandbox", you can test in that environment.

## Getting Started
To use this utility:
1. Open a terminal and navigate to the directory where you pulled this repo
2. Run `pip install requirements.txt` (Make sure Python is installed)
3. Gather a csv file of the invoices you would like created (Must have at least three columns, look at `example.csv` for reference)
4. Change the config variables at the top of `script.py` to your liking in accordance with your csv
5. If you don't already have an app at https://developer.intuit.com/app/developer/dashboard, create one
6. Get an Access Token using your client ID and secret. Go here to generate it: https://developer.intuit.com/app/developer/playground (You need the `com.intuit.quickbooks.accounting` scope)
    <img width="350" alt="Screen Shot" src="https://user-images.githubusercontent.com/45152459/152077032-e6cb2151-cec9-4f84-913b-6fe7d29059f4.png">
7. Get your Prod Company ID by going here: https://accounts.intuit.com/app/account-manager/productsBilling
8. Input your Quickbooks API credentials into a file called credentials.json (look at `example_credentials.json` for reference)
9. Run the script (If you did all of the above right, you shuldn't see any errors)
10. The script will create all of the requested invoices in QuickBooks and a new file called `invoices.txt` with the numbers of all invoices created, separated by newlines
11. KEEP IN MIND: This script only creates the invoices, it does not send them! If you want to send them out make sure to do that from the QB interface
