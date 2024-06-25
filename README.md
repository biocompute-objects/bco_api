# BCO DB
The BioCompute Database is designed to be deployable in a variety of environments. If configured properly it should work with the [BioCompute Portal](https://biocomputeobject.org/) reguardelss of the deployment. 

The BCO API repository contains a top-level folder “admin_only” which contains service definitions for gunicorn and django, an example database, and a prepopultated `.secrets` file (called `local_deployment.secrets`). 

The service definitions are for deployment on a server exposed to the internet. A local deployment will not need to use those files. Below are links to instructions for deployment in different environments. 

## BCODB Deployment

- [Local deployment](docs/deployment/localDeployment.md) 
    - For develpment or internal use only
- [Production deployment](docs/deployment/productionDeployment.md)
    - For deployment that is exposed to the internet
- [Docker deployment](docs/deployment/dockerDeployment.md)
    - WIP: comming soon

## BCODB Development and troubleshooting
- [FAQ and trouble shooting](docs/faq.md)
- [`.secretes` configuration](docs/config.md)
- [Testing](docs/testing.md)