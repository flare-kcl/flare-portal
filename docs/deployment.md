# Flare Portal — hosts and deployment

FLARe Portal is deployed on Heroku under Torchbox's Heroku account. Access is
granted only to authorized personnel.

## Login to Heroku

Please log in to Heroku before executing any commands for servers hosted there
using the `Heroku login -i` command. You have to do it both in the VM and your
host machine if you want to be able to use it in both places.

## Connect to the shell

To open the shell of the servers.

```bash
fab dev-shell
fab staging-shell
fab production-shell
```

## Scheduled tasks

When you set up a server you should make sure the following scheduled tasks are set.

- `django-admin clearsessions` - once a day (not necessary, but useful).
