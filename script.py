import requests
import json
import pandas as pd
import time

#Path to csv
csv_file_path = '/Users/coopergarren/Downloads/dues_data.csv'

#Dues item names in QB
dues_nonres_card = 'Dues (Non-Resident, card)'
dues_nonres_bank = 'Dues (Non-Resident)'
dues_nonres_check = 'Dues (Non-Resident)'
dues_res_card = 'Dues (Resident, card)'
dues_res_bank = 'Dues (Resident)'
dues_res_check = 'Dues (Resident)'

#Payment names in CSV
payment_header_string = 'How will you pay?'
bank_string = 'Bank transfer (enter account and routing numbers)'
card_string = "Credit card (3% service fee)"
check_string = "Check"

#Dues names in CSV
resident_header_string = 'Resident?'
resident_string = 'True'
nonresident_string = 'False'

#Email header name in CSV
email_header_string = 'Email Address'

#Due Date
due_date = "2021-10-12"

def post_request(url, thedata, env):
	#url = 'https://www.w3schools.com/python/demopage.php'
	#myobj = {'somekey': 'somevalue'}

	company_id = ""
	secret = ""

	with open('credentials.json') as f:
		data = json.load(f)
		#company_id = data["company-id"]
		auth_token = data[env]["auth-token"]

	#url = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' + company_id + '/companyinfo/' + company_id + '?minorversion=12'

	#print(url)

	theheaders = {}
	theheaders["accept"] = "application/json"
	theheaders["authorization"] = "Bearer " + auth_token
	theheaders["content-type"] = "application/json"

	#print(theheaders)

	req = requests.post(url, data = thedata, headers = theheaders)

	return req

def get_request(url, params, env):
	#url = 'https://www.w3schools.com/python/demopage.php'
	#myobj = {'somekey': 'somevalue'}

	company_id = ""
	secret = ""

	with open('credentials.json') as f:
		data = json.load(f)
		#company_id = data["company-id"]
		auth_token = data[env]["auth-token"]

	#url = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' + company_id + '/companyinfo/' + company_id + '?minorversion=12'

	#print(url)

	theheaders = {}
	theheaders["accept"] = "application/json"
	theheaders["authorization"] = "Bearer " + auth_token
	theheaders["content-type"] = "application/json"

	#print(theheaders)

	res = requests.post(url, headers = theheaders, params = params)

	return res

def create_invoice(customer_id, customer_name, customer_email, item_id, item_name, item_amount, item_unit_price, item_quantity, item_description, card_on, bank_on, due_date):
	#print(item_description, item_quantity, item_unit_price)
	params = {
	    "CustomerRef": {
	        "value": customer_id,
	        "name": customer_name
	    },
	    "Line": [
	        {
	            "DetailType": "SalesItemLineDetail",
	            "Amount": item_amount,
	            "Description": item_description,
	            "SalesItemLineDetail": {
	                "ItemRef": {
	                    "name": item_name,
	                    "value": item_id,
	                },
	                "Qty": item_quantity,
	                "UnitPrice": item_unit_price
	            }
	        }
	    ]
	}
	#print(params)
	create_res = post_request('https://quickbooks.api.intuit.com/v3/company/193514578775999/invoice', json.dumps(params), "prod")
	#print(create_res.text)
	create_res = json.loads(create_res.text)

	update_params = {
		"SyncToken": create_res["Invoice"]["SyncToken"],
		"sparse": True,
		"DueDate": due_date,
		"DocNumber": create_res["Invoice"]["Id"],
		"Id": create_res["Invoice"]["Id"],
		"AllowOnlineCreditCardPayment": card_on,
		"AllowOnlineACHPayment": bank_on,
		"BillEmail": {
			"Address": customer_email
		}
	}
	update_res = post_request('https://quickbooks.api.intuit.com/v3/company/193514578775999/invoice', json.dumps(update_params), "prod").text
	return json.loads(update_res)

def query_customer(email_address):
	params = {"query": "select * from Customer Where PrimaryEmailAddr = '" + email_address + "'"}
	res = get_request("https://quickbooks.api.intuit.com/v3/company/193514578775999/query", params, "prod")
	if res.status_code == 401:
		raise Exception('\033[91m401 Unauthorized, please refresh Quickbooks access token\033[0m')
	elif res.status_code != 200:
		raise Exception('\033[91mError Retriving data from Quickbooks\033[0m')
	return json.loads(res.text)

def query_line_item(name):
	params = {"query": "select * from Item Where Name = '" + name + "'"}
	res = get_request("https://quickbooks.api.intuit.com/v3/company/193514578775999/query", params, "prod")
	if res.status_code == 401:
		raise Exception('\033[91m401 Unauthorized, please refresh Quickbooks access token\033[0m')
	elif res.status_code != 200:
		raise Exception('\033[91mError Retriving data from Quickbooks\033[0m')
	return json.loads(res.text)

def parse_data(path):
	mydata = pd.read_csv(path)
	data_dict = mydata.to_dict(orient='records')
	return data_dict

print("Reading file...")
bro_data = parse_data(csv_file_path)

print("Gathering info from Quickbooks...")
dues_res_bank_id = query_line_item(dues_res_bank)
dues_res_card_id = query_line_item(dues_res_card)
dues_res_check_id = query_line_item(dues_res_check)
dues_nonres_bank_id = query_line_item(dues_nonres_bank)
dues_nonres_card_id = query_line_item(dues_nonres_card)
dues_nonres_check_id = query_line_item(dues_nonres_check)

print("Creating invoices...")
invoice_list = []
i=0
for bro in bro_data:
	email_address = bro[email_header_string]
	query_results = query_customer(email_address)

	customer_name = query_results['QueryResponse']['Customer'][0]["DisplayName"]
	customer_id = query_results['QueryResponse']['Customer'][0]["Id"]
	customer_email = email_address
	customer_payment = str(bro[payment_header_string])
	customer_resident = str(bro[resident_header_string])

	line_item = {}
	card_on = False
	bank_on = False

	if customer_payment == bank_string and customer_resident == resident_string:
		line_item = dues_res_bank_id
		bank_on = True
	elif customer_payment == bank_string and customer_resident == nonresident_string:
		line_item = dues_nonres_bank_id
		bank_on = True
	elif customer_payment == check_string and customer_resident == resident_string:
		line_item = dues_res_check_id
	elif customer_payment == check_string and customer_resident == nonresident_string:
		line_item = dues_nonres_check_id
	elif customer_payment == card_string and customer_resident == resident_string:
		line_item = dues_res_card_id
		card_on = True
	elif customer_payment == card_string and customer_resident == nonresident_string:
		line_item = dues_nonres_card_id
		card_on = True
	else:
		#print(customer_name, customer_resident, customer_payment, card_string)
		raise Exception('There was an issue parsing the following record: ' + customer_name)
	print(customer_name)
	print(" >", line_item['QueryResponse']['Item'][0]["Name"])
	print(" >", "$" + str(line_item['QueryResponse']['Item'][0]["UnitPrice"]))
	#print("->", "Bank:", bank_on)
	#print("->", "Card:", card_on)
	#print(line_item)
	# if customer_name == "Cooper Garren":
	res = create_invoice(customer_id, customer_name, customer_email, line_item['QueryResponse']['Item'][0]["Id"], line_item['QueryResponse']['Item'][0]["Name"], line_item['QueryResponse']['Item'][0]["UnitPrice"], line_item['QueryResponse']['Item'][0]["UnitPrice"], 1, line_item['QueryResponse']['Item'][0]["Description"], card_on, bank_on, due_date)
	invoice_list.append(res["Invoice"]["Id"])
	print("\033[92m >", "Invoice created\033[0m")
	
print("\033[95m" + str(len(bro_data)), "invoices created\033[0m")

print("Writing invoice id's to file...")
with open('./invoices.txt', 'w') as file:
	for invoice_id in invoice_list:
		file.write(str(invoice_id) + "\n")

print("Done")
