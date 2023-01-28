FROM jupyter/tensorflow-notebook

COPY ./core/requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

COPY ./ml/requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

RUN fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

RUN mkdir core
COPY ./core/ ./core/
COPY ./shared/ ./core/

RUN mkdir ml
COPY ./ml/ ./ml/
COPY ./shared/ ./ml/

USER $NB_UID

EXPOSE 8888

# Configure container startup
ENTRYPOINT ["tini", "-g", "--"]
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
