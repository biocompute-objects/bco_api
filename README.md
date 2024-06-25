# BCO DB
The BioCompute Database is designed to be deployable in a variety of environments. 

## BCODB Quickstart

The BCO API repository contains a top-level folder “admin_only” which contains service definitions for gunicorn and django, an example database, and a prepopultated `.secrets` file (called `local_deployment.secrets`). 

The service definitions are for deployment on a server exposed ot the internet. A local deployment will not need to use those files. Below are links to deployment instructions in different environments. 

- [Local deployment for devleopment](docs/localDeployment.md)
- [Production deployment](docs/productionDeployment.md)
- [Docker deployment](docs/dockerDeployment.md) [WIP]
- [FAQ and trouble shooting](docs/faq.md)



## Issues and BCODB Development