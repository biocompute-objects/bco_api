## BCO API Test

## Requirements

- Git
- Python 3.9
- VIM or other editor
- SQLite3

## First-time installation

```shell
ssh -i /Users/hadleyking/Box/Mazumdar_Lab/BCO_org/configsEC2/galaxydev.pem ec2-user@ec2-100-25-177-83.compute-1.amazonaws.com
sudo dd if=/dev/zero of=/var/myswap bs=1M count=4096
sudo mkswap /var/myswap
sudo swapon /var/myswap
sudo yum install nginx
sudo yum update -y
sudo yum install git -y
sudo yum -y install bzip2-devel libffi-devel openssl-devel
sudo yum groupinstall "Development Tools" -y

sudo useradd beta_portal_user
sudo passwd beta_portal_user
sudo usermod -a -G wheel beta_portal_user
su - beta_portal_user

git clone https://github.com/biocompute-objects/bco_api
	Cloning into 'bco_api'...
	Username for 'https://github.com':
	Password for 'https://HadleyKing@github.com':
```

### Get SQLite WITH the autoconfiguration option.

```shell
cd
wget https://sqlite.org/2021/sqlite-autoconf-3340100.tar.gz
tar -xvf sqlite-autoconf-3340100.tar.gz
```

### Configure

````shell
cd sqlite-autoconf-3340100/
LDFLAGS="-L${HOME}/opt/lib" CFLAGS="-L${HOME}/opt/include" ./configure --prefix=$HOME/opt
make && make install

### Remove downlaods
```shell
cd
rm -rf sqlite-autoconf-3340100*
````

### Compile Python 3.9 with the just-installed sqlite3

https://stackoverflow.com/a/63938144/7136900

```shell
cd
wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tar.xz
tar -xf Python-3.9.1.tar.xz
cd Python-3.9.1
LD_RUN_PATH=$HOME/opt/lib ./configure --enable-optimizations LDFLAGS="-L$HOME/opt/lib" CPPFLAGS="-I$HOME/opt/include" --prefix=$HOME/opt
LD_RUN_PATH=$HOME/opt/lib make && make altinstall
```

### Remove the python folders, to path, and ~/.bashrc

```shell
cd ~
rm -rf Python-3.9.1*
export PATH=~/opt/bin:$PATH
echo 'export PATH=~/opt/bin:$PATH' >> ~/.bashrc
```

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

- bco_api.socket
- bco_api.conf
- bco_api.service
- Make SSL sefl signed cert and key (https://devcenter.heroku.com/articles/ssl-certificate-self)

#### Service definition

The service file for the API is located in /home/beta_portal_user/bco_api/admin_only/bco_api.service. On CentOS, this should be copied to /etc/systemd/system/bco_api.service,

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
