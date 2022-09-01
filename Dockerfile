FROM ubuntu:22.04
LABEL org.opencontainers.image.source https://github.com/biocompute-objects/bco_api
ENV DEBIAN_FRONTEND=noninteractive

# Note that this is just for debug / test purposes; should not be set via the setup for production
ENV DJANGO_SUPERUSER_PASSWORD="BioCompute123"
ENV DJANGO_SUPERUSER_USERNAME="BioComputeSuperUser"
ENV DJANGO_SUPERUSER_EMAIL="BioComputeSuperUser@gwu.edu"

RUN apt-get -qq update && apt-get install -y python3.9 python3-dev python3-pip

RUN python3 -m pip install --upgrade pip

WORKDIR /biocompute_api

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

# COPY admin_only ./admin_only
COPY bco_api ./bco_api
#COPY static ./static
# COPY docs ./docs

WORKDIR /biocompute_api/bco_api

RUN python3 manage.py migrate
RUN python3 manage.py createsuperuser --no-input

EXPOSE 8000
#CMD ["bash"]
ENTRYPOINT ["python3", "manage.py", "runserver"]
CMD ["0.0.0.0:8000"]