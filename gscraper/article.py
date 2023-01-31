from dataclasses import dataclass

import serpapi


@dataclass
class Article:
	article_id: int
	cites_id: str
	publication_year: int
	service: str
	version: str
	article_url: str

	def __post_init__(self):
		self.article_id = int(self.article_id)
		self.publication_year = int(self.publication_year)

	def request_gs_citations(self, template_params, years):

		citations = {}
		start_year = max(years[0], self.publication_year)
		years_to_poll = range(start_year, years[1] + 1)

		params = dict(template_params)
		params["cites"] = self.cites_id

		if self.publication_year < start_year:
			params["as_yhi"] = str(start_year - 1)
			citations[start_year - 1] = serpapi.search_request(params)

		for year in years_to_poll:
			params["as_yhi"] = params["as_ylo"] = str(year)
			citations[year] = serpapi.search_request(params)

		return citations