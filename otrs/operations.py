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
    except ConnectorError as e:
        raise e

    try:
        title = params.get("title")
        queue = params.get("queue")
        state = params.get("state")
        priority = params.get("priority")
        customer = params.get("customer")
        article_subject = params.get("article_subject")
        article_body = params.get("article_body")
        ticketType = params.get('newTicketType')
        newDynamicField = params.get('newDynamicField')
        ticket = pyotrs.Ticket.create_basic(Title=title, Queue=queue, State=state, Priority=priority, CustomerUser=customer, Type=ticketType)
	if params["newDynamicField"]:
	    logger.debug('PARAMS {0}'.format(str(params["newDynamicField"])))
            dynamicFieldsParameter = params["newDynamicField"]
	    dFields = []
            for item in dynamicFieldsParameter:
                logger.debug('ITEM {0}'.format(str(item)))
                name = item['Name']
                value = item['Value']
                dFields.append(pyotrs.DynamicField(str(name), str(value)))
            logger.debug('dFields {0}'.format(str(dFields)))
        if not article_subject:
            article_subject = title
        ticket_article = pyotrs.Article({"Subject": article_subject, "Body": article_body})
        ticket_info = client.ticket_create(ticket, ticket_article, dynamic_fields=dFields)

        return {"ticket_metadata": ticket_info}
    except Exception as e:
        error_message = "Error creating OTRS ticket. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def update_ticket(config, params):
    logger.error('PARAMS {0}'.format(params))
    try:
        client = _create_client(config)
    except ConnectorError as e:
        raise e

    try:
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
        if params.get("oTRSArticle"):
            newArticle = pyotrs.Article(params.get("oTRSArticle"))
            update_params.update(article=newArticle)
            
        if params["dynamicField"]:
            logger.debug('PARAMS {0}'.format(str(params["dynamicField"])))
            dynamicFieldsParameter = params["dynamicField"]
            dFields = []
            for item in dynamicFieldsParameter:
              logger.debug('ITEM {0}'.format(str(item)))
              name = item['Name']
              value = item['Value']
              dFields.append(pyotrs.DynamicField(str(name), str(value)))
            logger.debug('dFields {0}'.format(str(dFields)))
            update_params.update(dynamic_fields=dFields)
            

        ticket_info = client.ticket_update(ticket_id, **update_params )

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
        states = params.get('state')
        title= params.get('title')
        ticketType=params.get('tickettype')
        logger.debug('state {0}'.format(str(states)))
        logger.debug('Ticket Type {0}'.format(str(ticketType)))
        timeSpanMinutes=str(params.get('timeSpanMinutes'))
        
        if states and ticketType:
          matching_tickets = client.ticket_search(States=states, Types=ticketType)
          return {"count": len(matching_tickets),"matches": matching_tickets}
		  
        if states:
          matching_tickets = client.ticket_search(States=states, Types=ticketType)
          return {"count": len(matching_tickets),"matches": matching_tickets}
        
        if timeSpanMinutes and title:
          matching_tickets = client.ticket_search(Title=title,TicketChangeTimeNewerMinutes=timeSpanMinutes,States=states,Types=ticketType)
          return {"count": len(matching_tickets),"matches": matching_tickets}
                
        if title:
          matching_tickets = client.ticket_search(Title=title,States=states,Types=ticketType)
          return {"count": len(matching_tickets),"matches": matching_tickets}
        
        if timeSpanMinutes:
          matching_tickets = client.ticket_search(TicketChangeTimeNewerMinutes=timeSpanMinutes,States=states,Types=ticketType)
          return {"count": len(matching_tickets), "matches": matching_tickets}
        
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
