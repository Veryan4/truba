FROM python:3.11-slim-buster AS compile-image

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY ./core/ .
COPY ./shared/ ./shared/
COPY ./schemas/ ./schemas/

RUN pip install -r requirements.txt
RUN datamodel-codegen  --input ./schemas/AllTypes.yaml --aliases ./schemas/aliases.json --output project_types.py

RUN pip install -r requirements-for-tests.txt
RUN pytest -vv tests
RUN cd .. && pip uninstall -y -r requirements-for-tests.txt

FROM python:3.11-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY ./core/ .
RUN rm -r ./tests
COPY ./shared/ ./shared/

RUN python ./shared/setup.py

CMD gunicorn --workers=4 --worker-class=uvicorn.workers.UvicornH11Worker --bind=0.0.0.0:5057 core:app
