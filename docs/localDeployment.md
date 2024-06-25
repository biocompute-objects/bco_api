# BCODB Local Deployment

## Clone the repository
```
git clone https://github.com/biocompute-objects/bco_api
```

**Make sure you are on the desired branch (Check for latest branch):**

```
git switch [DESIRED BRANCH TAG]
```

## Enter the repository, create a virtual environment, and install the required packages
```
cd bco_api

pyenv local 3.10.6

python3 -m venv env

source env/bin/activate

python -m pip install -r requirements.txt 
```

(You can use python3 if you’d like, but since you’re in the virtual environment you created python points to python3.10.6)

## Modify the Config files:
Check/Edit the server.conf file
This is the main server configuration file for the BCO API. (most of these values will NOT need to be changed for local deployment)

vim bco_api/bco_api/server.conf

Production and publishing flags NOTE: Valid values are True or False (note the capitalization).

[PRODUCTION]
production=False
DB Version

[VERSION]
version=22.01
Is this a publish-only server?

[PUBLISHONLY]
publishonly=False
Security settings: Create a key for an anonymous public user.

[KEYS]
anon=627626823549f787c3ec763ff687169206626149
Which host names do you want to associate with the server? Note: the local hostname (i.e. 127.0.0.1) should come at the end.

[HOSTNAMES]
prod_names=test.portal.biochemistry.gwu.edu,127.0.0.1
names=127.0.0.1:8000,127.0.0.1
Give the human-readable hostnames

[HRHOSTNAME]
hrnames=BCO Server (Default)
The public hostname of the server (i.e. the one to make requests to)

[PUBLICHOSTNAME]
prod_name=https://test.portal.biochemistry.gwu.edu
name=http://127.0.0.1:8000
Who gets to make requests?

[REQUESTS_FROM]
portal=https://test.portal.biochemistry.gwu.edu
local_development_portal=http://127.0.0.1:3000,http://localhost:3000
public=true
Namings: How do you want to name your objects?

[OBJECT_NAMING]
prod_root_uri=https://test.portal.biochemistry.gwu.edu
root_uri=http://127.0.0.1:8000
prod_uri_regex=root_uri/prefix_(\d+)/(\d+).(\d+)
uri_regex=root_uri/prefix_(\d+)/(\d+).(\d+)
**Requests ** Where are the request templates defined?

[REQUESTS]
folder=../api/request_definitions/
Where are the validation templates defined?

[VALIDATIONS]
folder=../api/validation_definitions/
Set up DB
cd bco_api/bco_api

Option #1: Use existing DB
Copy the dev db

cp ../admin_only/db.sqlite3.dev db.sqlite3

superusername: bco_api_user
password: testing123
Make Migrations

python3 manage.py migrate

Option #2: Create a new DB
Make Migrations

python3 manage.py migrate

Create a super user for the API:

python3 manage.py createsuperuser

Then follow the prompts

Then: Do a quick check to make sure the server can run
Start the server

python3 manage.py runserver 8000

Make sure API is accessible via web browser.

[YOU WEB HOST HERE]/api/admin/

EX: http://localhost:8000/api/admin/

If it worked you should be able to login using the SuperUser credentials you created above

Log in with the superuser credentials you created or imported

If you copied over the existing dbs you should be able to log in with any of the crednetials listed in /portal_userdb/server/admin/users.tsv

Otherwise you will have to register a new user.