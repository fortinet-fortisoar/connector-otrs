import requests, json
import pyotrs
#from pyotrs import Ticket, Article, Client
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('otrs')


def _create_client(config, **kwargs):
    try:
        client = pyotrs.Client(config["url"], config["username"], config["password"])
        client.session_create()
        return client
    except Exception as e:
        error_message = "Error creating OTRS client. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def create_ticket(config, params):
    try:
        client = _create_client(config)
    except ConnectorError as e:
        raise e

    try:
        title = params["title"]
        queue = params["queue"]
        state = params["state"]
        priority = params["priority"]
        customer = params["customer"]
        article_subject = params["article_subject"]
        article_body = params["article_body"]

        ticket = pyotrs.Ticket.create_basic(Title=title, Queue=queue, State=state, Priority=priority, CustomerUser=customer)
        if not article_subject:
            article_subject = title
        ticket_article = pyotrs.Article({"Subject": article_subject, "Body": article_body})
        ticket_info = client.ticket_create(ticket, ticket_article)

        return {"ticket_metadata": ticket_info}
    except Exception as e:
        error_message = "Error creating OTRS ticket. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def update_ticket(config, params):
    try:
        client = _create_client(config)
    except ConnectorError as e:
        raise e

    try:
        ticket_id = params["ticket_id"]
        update_params = {}
        if params["title"]:
            update_params.update({"Title": params["title"]})
        if params["queue"]:
            update_params.update({"Queue": params["queue"]})
        if params["state"]:
            update_params.update({"State": params["state"]})
        if params["priority"]:
            update_params.update({"Priority": params["priority"]})
        if params["customer"]:
            update_params.update({"CustomerUser": params["customer"]})
        if params["article_subject"] and params["article_body"]:
            new_article = pyotrs.Article({"Subject": params["article_subject"], "Body": params["article_body"]})
            update_params.update({"article": new_article})

        ticket_info = client.ticket_update(ticket_id, **update_params)

        return {"ticket_metadata": ticket_info}
    except Exception as e:
        error_message = "Error updating ticket {0}. Error message as follows:\n{1}".format(ticket_id, str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def get_ticket(config, params):
    try:
        client = _create_client(config)
    except ConnectorError as e:
        raise e

    try:
        ticket_id = params["ticket_id"]
        ticket = client.ticket_get_by_id(ticket_id, articles=True, attachments=False, dynamic_fields=True)

        return {"ticket": ticket.to_dct()}
    except Exception as e:
        error_message = "Error fetching OTRS ticket {0}. Error message as follows:\n{1}".format(ticket_id, str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def search_tickets(config, params):
    try:
        client = _create_client(config)
    except ConnectorError as e:
        raise e

    try:
        title = params["title"]
        matching_tickets = client.ticket_search(Title=title)

        return {"count": len(matching_tickets),
                "matches": matching_tickets}
    except Exception as e:
        error_message = "Error performing ticket search. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def check_health(config):
    logger.info("health check started")
    try:
        client = _create_client(config)
        return True
    except Exception as e:
        error_message = "Error in health check. Error message as follows:{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


operations = {
    'create_ticket': create_ticket,
    'update_ticket': update_ticket,
    'get_ticket': get_ticket,
    'search_tickets': search_tickets,
    'check_health': check_health
}