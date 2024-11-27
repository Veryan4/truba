FROM python:3.12-slim AS compile-image

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./ml/requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.12-slim AS build-image
COPY --from=compile-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY ./ml/ .
COPY ./schemas/ ./schemas/

RUN datamodel-codegen  --input ./schemas/AllTypes.yaml --aliases ./schemas/aliases.json --output project_types.py

CMD gunicorn --workers=4 --worker-class=uvicorn.workers.UvicornH11Worker --bind=0.0.0.0:5158 controller:app

#CMD python training.py