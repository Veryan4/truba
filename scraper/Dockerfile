FROM python:3.12-slim AS build-image

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

COPY ./scraper/requirements.txt ./requirements.txt
RUN pip install -U pip setuptools wheel
RUN pip install -r requirements.txt

#COPY ./scraper/requirements-for-tests.txt ./requirements-for-tests.txt
#RUN pip install -r requirements-for-tests.txt
RUN python -m spacy download en_core_web_sm 
RUN python -m spacy download fr_core_news_sm

COPY ./scraper/ .
COPY ./schemas/ ./schemas/

RUN datamodel-codegen  --input ./schemas/AllTypes.yaml --aliases ./schemas/aliases.json --output project_types.py

#RUN pytest -vv tests
#RUN cd .. && pip uninstall -y -r requirements-for-tests.txt
RUN rm -r ./tests

CMD python main.py