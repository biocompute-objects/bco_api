FROM ubuntu:21.04
ENV DEBIAN_FRONTEND=noninteractive

# Note that this is just for debug / test purposes; should not be set via the setup for production
ENV DJANGO_SUPERUSER_PASSWORD="BioCompute123"
ENV DJANGO_SUPERUSER_USERNAME="BioComputeSuperUser"
ENV DJANGO_SUPERUSER_EMAIL="BioComputeSuperUser@gwu.edu"

RUN apt-get -qq update && apt-get install -y python3 python3-dev python3-pip

RUN python3.9 -m pip install --upgrade pip

WORKDIR /biocompute_api

COPY requirements.txt .
COPY apitests.py .
COPY apitests_new.py .

RUN python3.9 -m pip install -r requirements.txt

COPY admin_only ./admin_only
COPY bco_api ./bco_api
#COPY static ./static
COPY docs ./docs

WORKDIR /biocompute_api/bco_api

RUN python3.9 manage.py migrate
RUN python3.9 manage.py loaddata ./api/fixtures/metafixtures.json
RUN python3.9 manage.py createsuperuser --no-input

#CMD ["bash"]
ENTRYPOINT ["python3.9", "manage.py", "runserver"]
CMD ["0.0.0.0:8000"]