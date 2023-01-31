import argparse
import json

from dataclasses import dataclass

import serpapi
from article import Article





def main():
	ap = argparse.ArgumentParser()
	# ap.add_argument("database", type=str)
	ap.add_argument("services_file", type=str)
	ap.add_argument("years", type=str)
	ap.add_argument("api_key", type=str)
	args = ap.parse_args()

	print(args)
	start_year, end_year = map(int, args.years.split("-"))
	
	query_params = dict(serpapi.api_params)
	query_params["api_key"] = args.api_key
	

	citation_counts = {}

	for i, line in enumerate(open(args.services_file, "rt")):
		if not i:
			continue

		article = Article(*line.strip().split("\t"))
		article_citations = article.request_gs_citations(query_params, (start_year, end_year))

		citation_counts.setdefault(article.service, {}).setdefault(article.cites_id, {})["annual_citations"] = article_citations

		print(article.service)
		if article.article_id > 0:
			break

	with open("citations.json", "wt") as json_out:
		json.dump(citation_counts, json_out)



if __name__ == "__main__":
	main()