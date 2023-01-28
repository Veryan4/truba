FROM tensorflow/tensorflow:2.9.1

COPY ./ml/requirements.txt .

RUN pip install -q tensorflow-recommenders
RUN pip install -q --upgrade tensorflow-datasets
RUN pip install -q scann
RUN pip install -r requirements.txt

COPY ./ml/ .
COPY ./shared/ ./shared/

RUN python ./shared/setup.py

CMD gunicorn --workers=4 --worker-class=uvicorn.workers.UvicornH11Worker --bind=0.0.0.0:5158 controller:app

#CMD python training.py