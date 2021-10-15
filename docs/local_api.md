## BCO API Test

## Requirements

- Git
- Python 3.9
- VIM or other editor
- SQLite3
- nginx
- gunicorn

## First-time installation

- git clone https://github.com/biocompute-objects/bco_api

### Create a virtual environment, activate it, and install the requirements.

```shell
cd ~/bco_api
python3.9 -m venv env
. env/bin/activate
pip3.9 install -r requirements.txt
```

### Make the migrations, migrate, and initialize tables

```shell
cd bco_api
python3.9 manage.py migrate
python3.9 manage.py loaddata ./api/fixtures/metafixtures.json
deactivate
```

cd bco_api
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
cd bco_api
python3 manage.py migrate
python3 manage.py loaddata ./api/fixtures/metafixtures.json
python3 manage.py createsuperuser
deactivate

````

### Switch back to beta_portal_user's home directory and change the ownership.
```shell
cd /home
chown ec2-user:nginx ec2-user -R
````

### Administrator steps

_update the service files_

#### Make SSL sefl signed cert and key (https://medium.com/@jonsamp/how-to-set-up-https-on-localhost-for-macos-b597bcf935ee)
- mkdir .localhost-ssl
- cd .localhost-ssl
- sudo openssl genrsa -out localhost.key 2048
- sudo openssl req -new -x509 -key localhost.key -out localhost.crt -days 3650 -subj /CN=localhost
- sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $PWD/localhost.crt

#### update the service files
- bco_api.socket
- bco_api.conf
- bco_api.service

#### Service definition

The service file for the API is located in /home/beta_portal_user/bco_api/admin_only/bco_api.service. 
On CentOS, this should be copied to /etc/systemd/system/bco_api.service. 

```shell
sudo cp /home/beta_portal_user/bco_api/admin_only/bco_api.service /etc/systemd/system/bco_api.service
sudo cp /home/beta_portal_user/bco_api/admin_only/bco_api.socket /etc/systemd/system/bco_api.socket
sudo systemctl enable bco_api
sudo systemctl start bco_api
```

#### Nginx configuration

**Note:** Make sure to suppress the default server settings that come with Nginx before using the provided configuration file.

- Within the configuration file, you’ll need to set the server IP and domain name. Note that all http requests are automatically forwarded to the corresponding https request.

- Copy the configuration file over to nginx and restart the service and the server

```shell
sudo cp /home/beta_portal_user/bco_api/admin_only/bco_api.conf /etc/nginx/conf.d/bco_api.conf
sudo systemctl restart nginx
l
```

\_**\_LOCAL RUN\_\_**

`python3 manage.py runserver`



##########

bco_api/bco_api/api/ -> ./rdb.sh -r
portal/userdb/portalusers/core/ -> ./rdb.sh -r
go to /portal/, npm run start
to go http://127.0.0.1:3000
go to http://localhost:3000/register -> fill out e-mail, username, password
copy temp_identifier from BCO API output in terminal, then create activation link (note encoded e-mail string): http://127.0.0.1:8000/api/accounts/activate/chrisarmstrong151%40gmail.com/f00d68462e0c4e758776b4a1dc5dd357
go to http://127.0.0.1:8000/login

copy temp id from django service 6fd97c393a0d4c49991d7e95ecd6ce71



^^^^^^^^^^^^^^^^^^^^^^
++++++++++++++++ TOKEN PROVIDED ++++++++++++++++
$$$$$$$$$$$$$ token_send $$$$$$$$$$$$$$$
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImhhZGxleWtpbmciLCJleHAiOjE2MjQwNDg0MzIsImVtYWlsIjoiaGFkbGV5X2tpbmdAZ3d1LmVkdSJ9.CD07y2kFVsol22jHlLYeLh5_uGePQNe5yAITTYGlskQ
HEADERS
{'Authorization': 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImhhZGxleWtpbmciLCJleHAiOjE2MjQwNDg0MzIsImVtYWlsIjoiaGFkbGV5X2tpbmdAZ3d1LmVkdSJ9.CD07y2kFVsol22jHlLYeLh5_uGePQNe5yAITTYGlskQ', 'Content-type': 'application/json; charset=UTF-8'}
DATA
@@@@@ USERNAME CHECK @@@@
hadley_king37
{"hostname": "127.0.0.1:8000", "human_readable_hostname": "BCO Server (Default)", "public_hostname": "http://127.0.0.1:8000", "token": "790a798bacf926b7198f8442d57395d21a1855eb", "username": "hadley_king37", "other_info": {"group_permissions": {"bco_drafters": ["Can add bco_draft", "Can change bco_draft", "Can delete bco_draft", "Can view bco_draft"], "bco_publishers": ["Can add bco_publish", "Can view bco_publish"], "hadley_king37": []}, "account_creation": "2021-06-18 20:31:22.709199+00:00", "account_expiration": ""}}
@@@@@ USERNAME CHECK @@@@
hadley_king37
R
<Response [200]>
[18/Jun/2021 20:31:23] "GET /api/accounts/activate/hadley_king%40gwu.edu/6fd97c393a0d4c49991d7e95ecd6ce71 HTTP/1.1" 200 879
Unauthorized: /favicon.ico
[18/Jun/2021 20:31:23] "GET /favicon.ico HTTP/1.1" 401 58

#### Local dev
1) start userdb on 8080
2) start BCODB on 8000
3) start portal on 3000


