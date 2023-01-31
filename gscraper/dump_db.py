import argparse
import datetime
import logging

from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql import func

from db.models import meta
from db.models.db import Article, Citations, Service

import serpapi


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s'
)

# sqlite> select service.name, citations.year_from, sum(citations.value) from citations join article on citations.article_id = article.id join service on article.service_id = service.id group by service.name, citations.year_from;

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("db", type=str)
	args = ap.parse_args()

	print(args)
	
	engine = create_engine(f"sqlite:///{args.db}")
	meta.Base.metadata.create_all(bind=engine)

	Session = sessionmaker(bind=engine)
	session = Session()


	citations = session.query(Service.name, Citations.year_from, func.sum(Citations.value))\
		.join(Article, Article.service_id == Service.id)\
		.join(Citations, Citations.article_id == Article.id)\
		.group_by(Service.name, Citations.year_from)\
		.all()

	year_from = session.query(func.min(Citations.year_from)).first()
	year_to = session.query(func.max(Citations.year_to)).first()
	years = tuple(range(year_from[0], year_to[0] + 1))

	services = tuple(service[0] for service in session.query(Service.name).all())

	print("service", *years, sep="\t")
		
	counts = {(service, year): count for service, year, count in citations}
	
	for service in services:
		print(service, *(counts.get((service, year), 0) for year in years), sep="\t")
	
	


		


if __name__ == "__main__":
	main()