# BCODB Production Update Deployment

**for instructions on deploying a NEW production instance see [newProductionInstance.md](/docs/newProductionInstance.md)

## Login to server and navigate to project root

Login example:
```
sh USER_NAME@test.portal.biochemistry.gwu.edu
cd /var/www/bcoeditor/bco_api
```

## Switch to and pull desired barnch
```
git fetch --all
git switch [DESIRED BRANCH]
```
## Update any configurations or settings required by the new version
- version in .secrets, etc.

## Restart the service
```
sudo systemctl restart bco_api
```
## Make the serive is running
```
sudo systemctl status bco_api
```

## Check that cahnges are live 
Navigate to `PROJECT-URL/api/docs/`. You should see the version value you entered in the `.secrets` file displayed on the Swagger page. 