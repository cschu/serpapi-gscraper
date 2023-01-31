# pylint: disable=R0903

""" module docstring """

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
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
	publication_year = Column(Integer)
	service_id = Column(Integer, ForeignKey("service.id"))
	service_version = Column(String)
	url = Column(String)

	service = relationship("Service", back_populates="articles")
	citations = relationship("Citations", back_populates="article")

	def request_gs_citations(self, template_params, year_to, year_from=None, full_update=False, request_f=None):
		citations = {}
		params = dict(template_params)
		params["cites"] = self.cites_id

		if year_from is None:
			# we want to have the 'historical aggregate' [Article.year, year_to]
			# which we can do by proxy as yhi = year_to and leaving ylo empty
			# note that setting ylo = Article.year may result in lower numbers
			# for the historical aggregate
			if year_to > self.publication_year:
				# we only query if article has existed for at least 1 year
				params["as_yhi"] = str(year_to)
				citations[(self.publication_year, year_to)] = request_f(params)
		elif year_from <= year_to:
			# query a range of years
			# ensure to start querying the years after the article was published
			years_to_poll = range(max(year_from, self.publication_year), year_to + 1)
			for i, year in enumerate(years_to_poll):
				if full_update and i == 0:
					params["as_yhi"] = str(year)
				elif full_update and year == year_to:
					try:
						del params["as_yhi"]
					except:
						pass
					params["as_ylo"] = str(year)
				else:
					params["as_yhi"] = params["as_ylo"] = str(year)
				citations[(year, year)] = request_f(params)

		return citations


	def request_gs_citations_old(self, template_params, years, request_f):
		print(years)
		citations = {}
		start_year = max(years[0], self.publication_year)
		years_to_poll = range(start_year, years[1] + 1)

		params = dict(template_params)
		params["cites"] = self.cites_id

		if self.publication < start_year:
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
	year_from = Column(Integer)
	year_to = Column(Integer)
	value = Column(Integer)
	query_date = Column(DateTime(timezone=True), server_default=func.now())

	article = relationship("Article", back_populates="citations")