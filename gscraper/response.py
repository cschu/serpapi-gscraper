import json

from collections import Counter
import itertools as it

cit_data = json.load(open("eggnog.json"))
print(cit_data)

start_year, end_year = 2019, 2022

def summarise_citation_data(cit_data, start_year, end_year):
	for tool, tool_pubs in cit_data.items():
		first_published = None
		cit_counts = Counter()
		for npub, (_, pub_data) in enumerate(tool_pubs.items(), start=1):
			pub_year = pub_data["publication_year"]
			first_published = min(pub_year, first_published) if first_published is not None else pub_year
			
			for year, citations in pub_data["annual_citations"].items():
				year = int(year)
				if year < start_year:
					cit_counts[f"<{start_year}"] += citations
				else:
					cit_counts[year] += citations

		yield (
			tool, first_published, npub,
			cit_counts[f"<{start_year}"],
		) + tuple((cit_counts[y] for y in range(start_year, end_year + 1)))
		

header = ["tool", "first_pub", "n_pubs", f"<{start_year}", *(str(y) for y in range(start_year, end_year + 1))]
print(*header, sep="\t")

for record in summarise_citation_data(cit_data, *(start_year, end_year)):
	print(*record, sep="\t")


