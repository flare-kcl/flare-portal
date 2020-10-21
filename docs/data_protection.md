# Flare Portal — Data Protection

This page gives an overview of potentially-sensitive data stored or processed by the Flare Portal project.

### User accounts

What personally-identifying data is stored in a user’s account?

### Other

Describe other stored or processed data here, and steps made to ensure this is compliant with GDPR, e.g.

- visitor enquiries
- user emails, e.g. newsletter subscription requests
- customer or purchase details
- stored Wagtail FormPage submissions

## Data locations

Where is the GDPR-related data stored? Does this include any backups, or exports?

### Exports

All exports include the above data. The first steps when downloading a copy of the production database, or cloning it to staging, should be to delete all records in the user-submitted tables:

```bash
$ python manage.py shell_plus
>>> FormSubmission.objects.all().delete()
```

When copying the data to staging, decide whether to leave user accounts intact: delete them if users are members of the public, don't if they're client employees who will still want to access the staging site. If using the data locally, you should anonymise user accounts:

```bash
$ python manage.py shell_plus
>>> for user in User.objects.all():
...     user.first_name = "User"
...     user.last_name = user.id
...     user.email = f"user.{user.id}@example.com"
...     user.username = f"user.{user.id}"
...     user.save()
```

## Responding to GDPR requests

If a request is received to purge or report the stored data for a given user, what steps are needed?

- For user account data, delete the user from the Wagtail admin
- For form submissions, ask the client to handle requests as the first option. Failing that, search the submissions and delete if necessary using the Django shell.
