import argparse
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


def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("db", type=str)
	ap.add_argument("years", type=str)
	ap.add_argument("api_key", type=str)
	args = ap.parse_args()

	print(args)
	
	start_year, *end_year = map(int, args.years.split("-"))
	
	end_year = end_year[0] if end_year else start_year
	
	query_params = dict(serpapi.api_params)
	query_params["api_key"] = args.api_key
	
	engine = create_engine(f"sqlite:///{args.db}")
	meta.Base.metadata.create_all(bind=engine)

	Session = sessionmaker(bind=engine)
	session = Session()

	for i, article in enumerate(session.query(Article).all()):

		print(str(article))
		raw_citations = article.request_gs_citations(query_params, (start_year, end_year), serpapi.search_request)  # if False else {2021: 790, 2022: 758}
		print(article.cites_id, article.service.name, raw_citations)

		for year, counts in raw_citations.items():
			# citations_obj = session.query(Citations).filter(Citations.article_id == article.id, Citations.year == year).one_or_none()
			citations_obj = session.query(Citations)\
				.filter(Citations.article_id == article.id, Citations.year == year)\
				.order_by(desc('query_date'))\
				.first()
			if citations_obj is None or counts != citations_obj.value:
				if citations_obj is not None and counts < citations_obj.value:
					logging.warning(f"Annual citation count for {year} for article {article.id} ({article.cites_id}) has decreased from {citations_obj.value} ({citations_obj.query_date}) to {counts}.")
				citations_obj = Citations(article_id=article.id, year=year, value=counts)
				session.add(citations_obj)
			
			session.commit()



		if i > 10:
			break




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