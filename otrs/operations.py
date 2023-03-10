""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import requests, json
import pyotrs
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('otrs')


def _create_client(config, **kwargs):
    try:
        client = pyotrs.Client(config["url"], config["username"], config["password"], https_verify=config["verify_ssl"])
        client.session_create()
        return client
    except Exception as e:
        error_message = "Error creating OTRS client. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def create_ticket(config, params):
    try:
        client = _create_client(config)
        title = params.get("title")
        queue = params.get("queue")
        state = params.get("state")
        priority = params.get("priority")
        customer = params.get("customer")
        article_subject = params.get("article_subject")
        article_body = params.get("article_body")
        update_params = {}

        if params.get("dynamicField"):
            name = params.get("dynamicField")['Name']
            value = params.get("dynamicField")['Value']
            df = pyotrs.DynamicField(name, value)
            update_params.update(dynamic_fields=[df])

        ticket = pyotrs.Ticket.create_basic(Title=title, Queue=queue, State=state, Priority=priority,
                                            CustomerUser=customer)
        if not article_subject:
            article_subject = title
        ticket_article = pyotrs.Article({"Subject": article_subject, "Body": article_body})
        update_params.update({"article": ticket_article})
        ticket_info = client.ticket_create(ticket, **update_params)

        return {"ticket_metadata": ticket_info}
    except Exception as Err:
        raise ConnectorError(Err)


def update_ticket(config, params):
    try:
        client = _create_client(config)
        ticket_id = params["ticket_id"]
        update_params = {}
        if params.get("title"):
            update_params.update({"Title": params["title"]})
        if params.get("queue"):
            update_params.update({"Queue": params["queue"]})
        if params.get("state"):
            update_params.update({"State": params["state"]})
        if params.get("priority"):
            update_params.update({"Priority": params["priority"]})
        if params.get("customer"):
            update_params.update({"CustomerUser": params["customer"]})
        if params.get("dynamicField"):
            name = params.get("dynamicField")['Name']
            value = params.get("dynamicField")['Value']
            df = pyotrs.DynamicField(name, value)
            update_params.update(dynamic_fields=[df])
        if params.get("article_subject") and params.get("article_body"):
            new_article = pyotrs.Article({"Subject": params.get("article_subject"), "Body": params.get("article_body")})
            update_params.update({"article": new_article})

        ticket_info = client.ticket_update(ticket_id, **update_params)

        return {"ticket_metadata": ticket_info}
    except Exception as Err:
        raise ConnectorError(Err)


def get_ticket(config, params):
    try:
        client = _create_client(config)
        ticket_id = params["ticket_id"]
        ticket = client.ticket_get_by_id(ticket_id, articles=True, attachments=False, dynamic_fields=True)

        return {"ticket": ticket.to_dct()}
    except Exception as Err:
        raise ConnectorError(Err)


def search_tickets(config, params):
    try:
        client = _create_client(config)
        state = params.get('state')
        title = params.get('title')
        ticketType = params.get('tickettype')

        matching_tickets = client.ticket_search(StateType=state, Types=ticketType)

        if title:
            matching_tickets = client.ticket_search(Title=title, StateType=state, Types=ticketType)

        return {"count": len(matching_tickets),
                "matches": matching_tickets}
    except Exception as Err:
        raise ConnectorError(Err)


def check_health(config):
    logger.info("health check started")
    try:
        client = _create_client(config)
        return True
    except Exception as Err:
        error_message = "Error in health check. Error message as follows:{0}".format(str(Err))
        logger.exception(error_message)
        raise ConnectorError(error_message)


operations = {
    'create_ticket': create_ticket,
    'update_ticket': update_ticket,
    'get_ticket': get_ticket,
    'search_tickets': search_tickets
}
