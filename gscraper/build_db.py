import argparse

from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.pool import StaticPool

from db.models import meta
from db.models.db import Article, Citations, Service

from article import Article as dc_Article

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("db", type=str)
	ap.add_argument("input_data", type=str)
	args = ap.parse_args()

	engine = create_engine(f"sqlite:///{args.db}")
	metadata = MetaData(engine)
	meta.Base.metadata.create_all(bind=engine)

	Session = sessionmaker(bind=engine)
	session = Session()

	for i, line in enumerate(open(args.input_data, "rt")):
		if i > 0:
			dc_article = dc_Article(*line.strip().split("\t"))

			service = session.query(Service).filter(Service.name == dc_article.service).one_or_none()
			if service is None:
				service = Service(name=dc_article.service)
				session.add(service)
				session.commit()
			
				print(f"Service {service.name} has id={service.id}.")

			article = session.query(Article).filter(Article.cites_id == dc_article.cites_id).one_or_none()
			if article is None:
				article = Article(
					cites_id=dc_article.cites_id,
					year=dc_article.publication_year,
					service_id=service.id,
					service_version=dc_article.version,
					url=dc_article.article_url,
				)

				session.add(article)
				session.commit()

			
			


if __name__ == "__main__":
	main()