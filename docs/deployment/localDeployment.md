# BCODB Local Deployment

## System Setup
### Requirements
- Python 3: [3.10.6 reccomended](https://www.python.org/downloads/release/python-3106/)
- [PyEnv](https://github.com/pyenv/pyenv) (optional but recommended fro Mac/Linux)

## Clone the repository
```
git clone https://github.com/biocompute-objects/bco_api
```

**Make sure you are on the desired branch (Check for latest branch):**

```
git switch [DESIRED BRANCH TAG]
```

## Enter the repository
```
cd bco_api
```

## Create a virtual environment and install the required packages

### For Mac/Linux:

*skip this first step if you do not want to use `pyenv`*
```
pyenv local 3.10.6
```

```
python3 -m venv env

source env/bin/activate

python -m pip install -r requirements.txt 
```

*If you are using `pyenv` and  you’re in the virtual environment you created using just `python` points to python3.10.6*

### For Windows:
```
`cd server`
`python -m venv env`
`source env/Scripts/activate`
`pip install -r requirements.txt`
```

## Configure the DB settings using the `.secrets` file:

### OPTION 1: Generate the secrets file 

In the project root copy the `.secrets.example` to `.secrets`

```
cp .secrets.example .secrets
```
#### Generate the DJANGO_KEY
Generate a 32-bytes long PSK key using the `openssl` command or `PowerShell` command.

##### Mac/Linux:
```
openssl rand -base64 32
```
##### Windows:
```   
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }) -as [byte[]])
```

Use a text editor to open the `.secrets` file update the rest of the values with the required values. For specifics see the [configuration](/docs/config.md) documentation. 

### OPTION 2: Use the `local_deployment.secrets` file
Fromt the project root:
```
cp admin_only/local_deployment.secrets .secrets
```

## Set up the databse
### Option #1: Use existing DB
This option will give you a working BCO DB with a couple of test users, existing BCOs, and some prefixes. 
```
cp admin/db.sqlite3 .
python3 manage.py migrate
```


superusername: bco_api_user
password: testing123
````

---
### Option #2: Create a new DB with test data
Create a DB:

`python3 manage.py migrate`

Load the DB with test data:

`python manage.py loaddata tests/fixtures/testing_data.json`

---
#### Run Server
`python3 manage.py runserver 8080`

Make sure API is accessible via web browser. EX: 
````
http://localhost:8080/users/admin/ 
````
If it worked you should be able to see the API Documentation site at:

`http://localhost:8080/users/docs/`












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