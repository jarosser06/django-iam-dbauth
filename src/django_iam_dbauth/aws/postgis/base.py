import getpass
import boto3

from django.contrib.gis.db.backends.postgis import base
from django_iam_dbauth.utils import resolve_cname


class DatabaseWrapper(base.DatabaseWrapper):
    def get_connection_params(self):
        params = super(DatabaseWrapper, self).get_connection_params()
        enabled = params.pop('use_iam_auth', None)
        if enabled:
            aws_region = params.pop('aws_region', None)
            client_args = {}
            if aws_region:
                client_args = {'region_name': aws_region}

            rds_client = boto3.client("rds", **client_args)

            hostname = params.get('host')
            hostname = resolve_cname(hostname) if hostname else "localhost"

            args = {
                'DBHostname': hostname,
                'Port': params.get("port", 5432),
                'DBUsername': params.get("user") or getpass.getuser(),
            }

            if aws_region:
                args['Region'] = aws_region
            params["password"] = rds_client.generate_db_auth_token(**args)

        return params
