# pylint: disable=R0903

""" module docstring """

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .meta import Base




class Service(Base):
	__tablename__ = "service"

	id = Column(Integer, primary_key=True)
	name = Column(String, index=True)

	articles = relationship("Article", back_populates="service")


class Article(Base):
	__tablename__ = "article"

	id = Column(Integer, primary_key=True)
	cites_id = Column(String, index=True)
	year = Column(Integer)
	service_id = Column(Integer, ForeignKey("service.id"))
	service_version = Column(String)
	url = Column(String)

	service = relationship("Service", back_populates="articles")
	citations = relationship("Citations", back_populates="article")

	def request_gs_citations(self, template_params, years, request_f):
		print(years)
		citations = {}
		start_year = max(years[0], self.year)
		years_to_poll = range(start_year, years[1] + 1)

		params = dict(template_params)
		params["cites"] = self.cites_id

		if self.year < start_year:
			params["as_yhi"] = str(start_year - 1)
			citations[start_year - 1] = request_f(params)

		for year in years_to_poll:
			params["as_yhi"] = params["as_ylo"] = str(year)
			citations[year] = request_f(params)

		return citations


class Citations(Base):
	__tablename__ = "citations"

	id = Column(Integer, primary_key=True)
	article_id = Column(Integer, ForeignKey("article.id"))
	year = Column(Integer)
	value = Column(Integer)
	query_date = Column(DateTime(timezone=True), server_default=func.now())

	article = relationship("Article", back_populates="citations")