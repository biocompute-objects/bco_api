FROM ubuntu:22.04
FROM python:3.10-slim-buster
LABEL org.opencontainers.image.source https://github.com/biocompute-objects/bco_api
LABEL org.opencontainers.image.description="The master repository for the JSON API."
LABEL org.opencontainers.image.licenses=MIT
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && apt-get install -y python3.10 python3-dev python3-pip

RUN python3 -m pip install --upgrade pip

WORKDIR /biocompute_api

COPY . ./

WORKDIR /biocompute_api/

RUN python3 -m pip install -r requirements.txt


EXPOSE 8000
ENTRYPOINT ["python3", "manage.py", "runserver"]
CMD ["0.0.0.0:8000"]