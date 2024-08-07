# BCODB Docker Deployment


### Requirements
- Python 3: [3.10.6 reccomended](https://www.python.org/downloads/release/python-3106/)
- [PyEnv](https://github.com/pyenv/pyenv) (optional but recommended for Mac/Linux)
- Docker:
    - [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/)
    - [Docker Desktop for Mac (macOS)](https://docs.docker.com/desktop/install/mac-install/)
    - [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)


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

Use a text editor to open the `.secrets` file and update the rest of the variables. For details on each of the variables see the [configuration](/docs/config.md) documentation. 

### OPTION 2: Use the `local_deployment.secrets` file
Fromt the project root:
```
cp admin_only/local_deployment.secrets .secrets
```

### Building the BCO API via Docker

A docker file is provided to allow easy building of the BCO API.  This can be done from the root directory (the directory with Dockerfile in it) by running:

`docker build -t bco_api:latest .`

This will build a container named `bco_api` with the tag `latest`.

The build process (via the `entrypoint.sh` script) will check for an existing database in the repository and run migrations. If no database is present one will be created and the test data will be loaded (taken from `config/fixtures/local_data.json`).

### Running the container via Docker

The BCO Api container can be run via docker on the command line in Linux/Windows by running:

`docker run --rm --network host -it bco_api:latest`

The BCO Api container can be run via docker on the command line in MacOS by running:

`docker run --rm -p 8000:8000 -it bco_api:latest`

This will expose the server at `http://127.0.0.1:8000`, whitch is where all of the default settings will expect to find the BCODB. 

#### Overriding the port

It is possible to override the port 8000 to whatever port is desired.  This is done by running the container with 8080 representing the desired port.

`docker run --rm --network host -it bco_api:latest 0.0.0.0:8080`


NOTE: The ip address of 0.0.0.0 is to allow the web serer to properly associate with 127.0.0.1 - if given 127.0.0.1 it will not allow communications outside of the container!

You can also give it a specific network created with `docker network create` if you wanted to give assigned IP addresses.
