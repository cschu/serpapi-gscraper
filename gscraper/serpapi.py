import json
import requests


api_params = {
	"engine": "google_scholar",
	"api_key": "",
	"hl": "en",
}

def search_request(params):
	print(params)
	r = requests.get(
		"https://serpapi.com/search",
		params=params
	)
	response = r.text
	try:
		return json.loads(response)["search_information"].get("total_results", 0)
	except Exception as err:
		print(response)
		raise ValueError(f"{err}") from err

def queries_left(api_key):
	r = requests.get(
		"https://serpapi.com/account",
		params={"api_key": api_key},
	)
	response = r.text
	try:
		return json.loads(response).get("plan_searches_left", -1)
	except Exception as err:
		print(response)
		raise ValueError(f"{err}") from err