FROM ubuntu:22.04
LABEL org.opencontainers.image.source https://github.com/biocompute-objects/bco_api
ENV DEBIAN_FRONTEND=noninteractive

LABEL org.opencontainers.image.source=https://github.com/octocat/my-repo
LABEL org.opencontainers.image.description="My container image"
LABEL org.opencontainers.image.licenses=MIT


RUN apt-get -qq update && apt-get install -y python3.9 python3-dev python3-pip

RUN python3 -m pip install --upgrade pip

WORKDIR /biocompute_api

COPY requirements.txt /biocompute_api/
RUN python3 -m pip install -r requirements.txt

COPY . /biocompute_api/

WORKDIR /biocompute_api

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
