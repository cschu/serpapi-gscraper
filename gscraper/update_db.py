import argparse
import datetime
import logging

from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import desc

from db.models import meta
from db.models.db import Article, Citations, Service

import serpapi


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s'
)

def load_citations(raw_citations, article, session):
	for (year_from, year_to), counts in raw_citations.items():
		# citations_obj = session.query(Citations).filter(Citations.article_id == article.id, Citations.year == year).
		citations_obj = session.query(Citations)\
			.filter(Citations.article_id == article.id, Citations.year_from == year_from, Citations.year_to == year_to)\
			.order_by(desc('query_date'))\
			.first()
		if citations_obj is None or counts != citations_obj.value:
			if citations_obj is not None and counts < citations_obj.value:
				logging.warning(f"Annual citation count for {year_from}-{year_to} for article {article.id} ({article.cites_id}) has decreased from {citations_obj.value} ({citations_obj.query_date}) to {counts}.")
			citations_obj = Citations(article_id=article.id, year_from=year_from, year_to=year_to, value=counts)
			session.add(citations_obj)			
			session.commit()



def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("db", type=str)
	ap.add_argument("years", type=str)
	ap.add_argument("api_key", type=str)
	ap.add_argument("--debug", action="store_true")
	args = ap.parse_args()

	print(args)
	
	query_params = dict(serpapi.api_params)
	query_params["api_key"] = args.api_key
	
	engine = create_engine(f"sqlite:///{args.db}")
	meta.Base.metadata.create_all(bind=engine)

	Session = sessionmaker(bind=engine)
	session = Session()

	if args.years == "full_update":
		year_from, year_to = None, datetime.datetime.now().year
	else:
		year_from, *year_to = map(int, args.years.split("-"))	
		year_to = year_to[0] if year_to else year_from
	

	for i, article in enumerate(session.query(Article).all()):

		if args.debug:
			raw_citations = {(2021, 2021): 560, (2022, 2022): 765, (2019, 2020): 231}
		elif year_from is not None:
			print(str(article))
			raw_citations = article.request_gs_citations(query_params, year_to=year_to, year_from=year_from, request_f=serpapi.search_request)  # if False else {(2000, 2021): 790, (2022, 2022): 758}
			print(article.cites_id, article.service.name, raw_citations)
			raw_citations.update(article.request_gs_citations(query_params, year_to=year_from - 1, request_f=serpapi.search_request))
			print(article.cites_id, article.service.name, raw_citations)
		else:
			# year_from = article.publication_year - 1
			raw_citations = article.request_gs_citations(query_params, year_to=year_to, year_from=article.publication_year, full_update=True, request_f=serpapi.search_request)
			print(article.cites_id, article.service.name, raw_citations)
			

		load_citations(raw_citations, article, session)



		# if i > -1:
		# 	break




	# for i, line in enumerate(open(args.input_data, "rt")):
	# 	if i > 0:
	# 		dc_article = dc_Article(*line.strip().split("\t"))

	# 		service = session.query(Service).filter(Service.name == dc_article.service).one_or_none()
	# 		if service is None:
	# 			service = Service(name=dc_article.service)
	# 			session.add(service)
	# 			session.commit()
			
	# 			print(f"Service {service.name} has id={service.id}.")

	# 		article = session.query(Article).filter(Article.cites_id == dc_article.cites_id).one_or_none()
	# 		if article is None:
	# 			article = Article(
	# 				cites_id=dc_article.cites_id,
	# 				year=dc_article.publication_year,
	# 				service_id=service.id,
	# 				service_version=dc_article.version,
	# 				url=dc_article.article_url,
	# 			)

	# 			session.add(article)
	# 			session.commit()

			
			


if __name__ == "__main__":
	main()