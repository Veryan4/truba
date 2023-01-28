FROM solr:8.4.1


COPY ./solr/solr.xml /var/solr/data/solr.xml
COPY ./solr/truba /opt/docker-solr/conf/

USER root
RUN chown solr:0 /var/solr/data/solr.xml
RUN chown -R 0:0 /opt/docker-solr/conf
USER solr

VOLUME /var/solr
EXPOSE 8983
WORKDIR /opt/solr

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["solr-precreate", "truba"]


#This is a copy of a Solr image with install plugins
