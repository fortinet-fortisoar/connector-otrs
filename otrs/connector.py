""""
Copyright start
MIT License
Copyright (c) 2023 Fortinet Inc
Copyright end
"""


from connectors.core.connector import Connector
from connectors.core.connector import get_logger, ConnectorError
from .operations import check_health, operations

logger = get_logger('otrs')


class Otrs(Connector):
    def execute(self, config, operation, params, **kwargs):
        try:
            action = operations.get(operation)
            return action(config, params)
        except Exception as Err:
            raise ConnectorError(Err)

    def check_health(self, config):
        try:
            return check_health(config)
        except Exception as Err:
            raise ConnectorError(Err)
