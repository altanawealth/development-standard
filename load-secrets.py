import os
import json
import requests
import boto3
from datetime import datetime
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
 
# JSON-based secrets module
with open(os.path.join(PROJECT_ROOT, "local.json")) as f:
    secrets = json.loads(f.read())
 
try:
    env = secrets['__ENVIRONMENT']
    if env == 'local' or env == "pipelines":
        DEBUG = True
    else:
        DEBUG = False
except BaseException:
    DEBUG = False
 

def get_secret(param_name):
    """
    This function reads a secure parameter from AWS' SSM service.
    The request must be passed a valid parameter name, as well as
    temporary credentials which can be used to access the parameter.
    The parameter's value is returned.
    In Local it reads the secret from local.json file
    """
    if DEBUG:
        try:
            return secrets[param_name]
        except KeyError:
            error_msg = "Set the {0} environment variable".format(param_name)
            raise ImproperlyConfigured(error_msg)
    else:
        try:
            return secrets[param_name]
        except Exception as e:
            error_msg = "Did not find the param (%s) in the local file (exception was %s %s), trying the AWS param store instead" % (param_name, type(e), str(e))
            print(error_msg)
            try:
                # Create the SSM Client
                ssm = boto3.client('ssm', region_name=secrets['AWS_S3_REGION'])
 
                # Get the requested parameter
                response = ssm.get_parameters(Names=[param_name, ], WithDecryption=True)
 
                # Store the credentials in a variable
                credentials = response['Parameters'][0]['Value']
                return credentials
            except BaseException:
                error_msg = "Set the {0} environment variable".format(param_name)
                raise ImproperlyConfigured(error_msg)
 
# Recaptcha Keys
try:
    RECAPTCHA_SITE_KEY = get_secret('RECAPTCHA_SITE_KEY')
except BaseException:
    RECAPTCHA_SITE_KEY = ""
