# BCODB Local Deployment

## System Setup
### Requirements
- Python 3: [3.10.6 reccomended](https://www.python.org/downloads/release/python-3106/)
- [PyEnv](https://github.com/pyenv/pyenv) (optional but recommended for Mac/Linux)

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

*If you are using `pyenv` and you’re in the virtual environment you created using just `python` points to python3.10.6*

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

## Set up the database
Both options will give you a working BCO DB with a couple of test users, existing BCOs, and some prefixes. 

The details for the test data is included in the 
### Option #1: Use existing DB

```
cp admin_only/db.sqlite3 .
python3 manage.py migrate
```

```
superusername: bco_api_user
password: testing123
````

---
### Option #2: Create a new DB with test data
Create a DB and load the DB with test data:
```
python3 manage.py migrate
python manage.py loaddata tests/fixtures/testing_data.json
```

---
## Run The Server
Start the Django server. 
```
python3 manage.py runserver
```

The BCO DB is designed to run on the default Django port `8000`. If you want to use another port you can specify that option at the end of the command: `python3 manage.py runserver 8181`

Make sure API is accessible via web browser. If it worked, you should be able to see the Django Admin site at:
```
http://localhost:8000/api/admin/
```
You should be able to log in with the superuser credentials you created or imported

If you copied over the existing databases you should be able to use any of the tokens[KEYs] listed in the [authtoken_token.tsv](/admin_only/test_database_tables/authtoken_token.tsv) table to submit requests via the [Swagger page](http://localhost:8000/api/docs/)

Otherwise you will have to create a new user.

## "What Can I Do Now?"

- Use the [Swagger Docs](http://localhost:8000/api/docs/) to develop or experiment with the APIs.
- Connect to the public [BCO Portal](https://biocomputeobject.org/).

