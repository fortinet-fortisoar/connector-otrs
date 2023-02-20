from connectors.core.connector import Connector
from connectors.core.connector import get_logger, ConnectorError
from .operations import operations

logger = get_logger('otrs')


class Otrs(Connector):

    def execute(self, config, operation, params, **kwargs):
        try:
            action = operations.get(operation)
            result = {}

            result = action(config, params)
            return result
        except Exception as e:
            error_message = "Error in execute(). Error message as follows: {0}".format(str(e))
            raise ConnectorError(error_message)


    def check_health(self, config):
        try:
            return operations.get("check_health")(config)
        except Exception as e:
            error_message = "Error in Health check. Error message as follows: {0}".format(str(e))
            raise ConnectorError(error_message)
