# Most of the settings are set in base.py, that's why this file appears fairly
# empty.
# Disable logging
import logging

from .base import *  # noqa

logging.disable(logging.CRITICAL)

SECRET_KEY = "test-key"
DEBUG = False
AUTH_PASSWORD_VALIDATORS = []
