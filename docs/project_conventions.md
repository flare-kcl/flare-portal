# Flare Portal project conventions

## Git branching model

This project loosely follows trunk-based development. When starting a new
feature, branch of from `main` and open a pull request. When pull requests are
merged, staging is automatically updated.

## Deploying to production

The process for deploying to production is as follows:

```
git checkout main
git pull  # Make sure it's up-to-date
git checkout production
git merge production
git push
```

CI will deploy the code in the `production` branch to the production Heroku app.

## Feature flags

As a consequence of our workflow, all code merged to `main` will eventually be
deployed to production. If there is some functionality you wish to disable on
production, make sure to gate them behind feature flags.

Please use environment variables and Django settings to configure feature flags.
