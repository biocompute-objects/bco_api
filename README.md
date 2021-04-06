# BCO API

There is one script for pulling the BCO API from github, cag.sh (Clone API from Github).  You must run the script with the --keep-db or --drop-db flag to keep or drop the existing database, respectively.

# Configuring the server

In the repository folder bco_api are two files, server.conf and tables.conf, which configure the server and the tables available on it, respectively.  The relevant settings in each of these are listed below.

### server.conf

[HOSTNAMES] - Change these to reflect the IP and domain name of your BCO API server.

[HRHOSTNAME] - Change this to reflect the human-readable name of your BCO API server.

### tables.conf

[JSON_OBJECT] - Put the models here that should be available on your server.

[META_TABLE] - Put a meta table for each of the models in [JSON_OBJECT].
