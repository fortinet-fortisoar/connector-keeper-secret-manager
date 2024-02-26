"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""

from connectors.core.connector import get_logger, ConnectorError
from keeper_secrets_manager_core import SecretsManager
from keeper_secrets_manager_core.storage import FileKeyValueStorage

logger = get_logger('keeper-secrets-manager')


class KeepersSecretManager:
    def __init__(self, config, connector_info, flag=None):
        self.token = config.get('credentials')
        self.verify_ssl = config.get('verify_ssl')
        try:
            if flag:
                file_name = config.get('name')
                self.secrets_manager = SecretsManager(
                    token=self.token,
                    config=FileKeyValueStorage(file_name),
                    verify_ssl_certs=self.verify_ssl
                )
                connector_info.update({'secrets_manager': self.secrets_manager})
            else:
                file_name = config.get('name')
                self.secrets_manager = SecretsManager(
                    config=FileKeyValueStorage(file_name),
                    verify_ssl_certs=self.verify_ssl
                )
                connector_info.update({'secrets_manager': self.secrets_manager})

        except Exception as e:
            raise ConnectorError("Failed to initialize KSM Client. " + str(e))
        self.headers = {'Content-Type': 'application/json'}

    def get_password_details(self, config, connector_info):
        try:
            records = connector_info.get('secrets_manager').get_secrets() or []
            return records
        except Exception as err:
            logger.exception("{0}".format(str(err)))
            raise ConnectorError("{0}".format(str(err)))

    def get_credentials_inner(self, config, params, connector_info):
        records, formatted_output = [], []
        all_secrets = connector_info.get('secrets_manager').get_secrets() or []
        for sec in all_secrets:
            records.append(sec.dict)
        if records:
            for r in records:
                if r.get('type') == "login":
                    formatted_output.append(
                        {
                            "key": r.get('title'),
                            "display_name": r.get('title')
                        }
                    )
        return formatted_output

    def get_credentials_details_inner(self, config, params, connector_info):
        formatted_output = []
        Object = params.get('secret_id')
        params.update({'title': Object})
        secret = connector_info.get('secrets_manager').get_secret_by_title(Object) or []
        if secret:
            records = secret.dict
            if records:
                for field in records.get('fields'):
                    formatted_output.append(
                        {
                            "field_name": field.get('type'),
                            "value": "*****"
                        }
                    )
        return formatted_output

    def get_credential_inner(self, config, params, connector_info):
        Object = params.get('secret_id')
        attribute_name = params.get('attribute_name')
        secret = self.secrets_manager.get_secret_by_title(Object) or []
        if secret:
            records = secret.dict
            if records:
                for field in records.get('fields'):
                    if field.get('type') == attribute_name:
                        return {
                            "password": field.get('value')[0]
                        }
                    else:
                        continue
                return {
                    "message": "Invalid Attribute"
                }


def get_password(config, params, connector_info):
    try:
        records = []
        ksm = KeepersSecretManager(config, connector_info=connector_info, flag=False)
        all_secrets = ksm.get_password_details(config, connector_info)
        for secret in all_secrets:
            records.append(secret.dict)
        return records
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def get_credentials(config, params, connector_info):
    try:
        ksm = KeepersSecretManager(config, connector_info=connector_info, flag=False)
        return ksm.get_credentials_inner(config, params=params, connector_info=connector_info)
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def get_credentials_details(config, params, connector_info):
    try:
        ksm = KeepersSecretManager(config, connector_info=connector_info, flag=False)
        return ksm.get_credentials_details_inner(config, params=params, connector_info=connector_info)
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def get_credential(config, params, connector_info):
    try:
        ksm = KeepersSecretManager(config, connector_info=connector_info, flag=False)
        return ksm.get_credential_inner(config, params=params, connector_info=connector_info)
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def _check_health(config, connector_info):
    try:
        ksm = KeepersSecretManager(config, connector_info=connector_info, flag=True)
        response = ksm.get_password_details(config, connector_info=connector_info)
        if response:
            return True
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


operations = {
    'get_password': [get_password],
    'get_credentials': [get_credentials],
    'get_credentials_details': [get_credentials_details],
    'get_credential': [get_credential]
}
