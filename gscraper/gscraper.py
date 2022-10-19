import json
import requests

from collections import Counter
import itertools as it


def make_request(params):
	r = requests.get(
		"https://serpapi.com/search",
		params=params
	)
	return json.loads(r.text)

def summarise_citation_data(cit_data, start_year, end_year):
	for tool, tool_pubs in cit_data.items():
		first_published = None
		cit_counts = Counter()
		for npub, (_, pub_data) in enumerate(tool_pubs.items(), start=1):
			pub_year = pub_data["publication_year"]
			first_published = min(pub_year, first_published) if first_published is not None else pub_year
			
			for year, citations in pub_data["annual_citations"].items():
				print(year, citations)
				year = int(year)
				if year < start_year:
					cit_counts[f"<{start_year}"] += citations
				else:
					cit_counts[year] += citations

		yield (
			tool, first_published, npub,
			cit_counts[f"<{start_year}"],
		) + tuple((cit_counts[y] for y in range(start_year, end_year + 1)))


params = {
	"engine": "google_scholar",
	"api_key": "",
	"hl": "en",
}

pubs = (
	("eggnog", 11926277896809258613, 2019),
	("eggnog", 10735210926890364446, 2017),
	("eggnog", 9989213968742927327, 2021),
	("eggnog", 10735210926890364446, 2017),
	("eggnog", 16178506737030708895, 2016),
	("eggnog", 11212564900201235579, 2012),
	("eggnog", 13237168627628146129, 2007),
	("eggnog", 13994930980074868413, 2014),
	("eggnog", 2416447087782313418, 2010),
)

years = (2019, 2022)

cit_counts = {}

for tool, cites_id, pub_year in pubs:
	cit_counts.setdefault(tool, {}).setdefault(cites_id, {})["publication_year"] = pub_year

	params["cites"] = str(cites_id)

	start_year = max(years[0], pub_year)
	years_to_poll = tuple(range(start_year, years[1] + 1))

	# grab citations < years[0]
	if pub_year < start_year:
		try:
			del params["as_ylo"]
		except KeyError:
			pass
		params["as_yhi"] = str(start_year - 1)
		resp = make_request(params)
		print(resp["search_information"])
		print(resp["search_parameters"])
		cit_counts.setdefault(tool, {}).setdefault(cites_id, {}).setdefault("annual_citations", {})[start_year - 1] = resp["search_information"]["total_results"]		

	for year in years_to_poll:
		params["as_yhi"] = params["as_ylo"] = str(year)
		resp = make_request(params)
		print(resp["search_information"])
		print(resp["search_parameters"])
		cit_counts.setdefault(tool, {}).setdefault(cites_id, {}).setdefault("annual_citations", {})[year] = resp["search_information"]["total_results"]

	#break

with open(f"{tool}.json", "wt") as _out:
	json.dump(cit_counts, _out)


header = ["tool", "first_pub", "n_pubs", f"<{start_year}", *(str(y) for y in range(years[0], years[1] + 1))]
print(*header, sep="\t")
for record in summarise_citation_data(cit_counts, *years):
	print(*record, sep="\t")


#break




#curl --get https://serpapi.com/search \
# -d engine="google_scholar" \
#-d cites="13457976773250883046" \
#-d api_key="" \
#-o test_string.json \
#-d num="10000"
