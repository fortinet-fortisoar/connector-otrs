""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import pyotrs
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('otrs')


def _create_client(config, **kwargs):
    try:
        client = pyotrs.Client(config.get("url"), config.get("username"), config.get("password"), https_verify=config.get("verify_ssl"))
        client.session_create()
        return client
    except Exception as e:
        error_message = "Error creating OTRS client. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def create_ticket(config, params):
    try:
        client = _create_client(config)
        data_fields = []
        title = params.get("title")
        queue = params.get("queue")
        state = params.get("state")
        priority = params.get("priority")
        customer = params.get("customer")
        article_subject = params.get("article_subject")
        article_body = params.get("article_body")
        ticket_type = params.get('newTicketType')
        article_sender_type = params.get("articleSenderType") if params.get("articleSenderType") else ''
        ticket = pyotrs.Ticket.create_basic(Title=title, Queue=queue, State=state, Priority=priority,
                                            CustomerUser=customer, Type=ticket_type)
        new_dynamic_field = params.get("newDynamicField")
        if new_dynamic_field:
            logger.debug('New Dynamic Field {0}'.format(new_dynamic_field))
            for item in new_dynamic_field:
                logger.debug('ITEM {0}'.format(str(item)))
                name = item['Name']
                value = item['Value']
                data_fields.append(pyotrs.DynamicField(str(name), str(value)))
            logger.debug('dFields {0}'.format(str(data_fields)))
        if not article_subject:
            article_subject = title
        ticket_article = pyotrs.Article({"Subject": article_subject, "Body": article_body, "MimeType": "text/html",
                                         "SenderType": article_sender_type})
        ticket_info = client.ticket_create(ticket, ticket_article, dynamic_fields=data_fields)

        return {"ticket_metadata": ticket_info}
    except ConnectorError as e:
        raise e
    except Exception as e:
        error_message = "Error creating OTRS ticket. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def update_ticket(config, params):
    ticket_id = params.get("ticket_id")
    try:
        client = _create_client(config)
        update_params = {}
        if params.get("title"):
            update_params.update({"Title": params.get("title")})
        if params.get("queue"):
            update_params.update({"Queue": params.get("queue")})
        if params.get("state"):
            update_params.update({"State": params.get("state")})
        if params.get("priority"):
            update_params.update({"Priority": params.get("priority")})
        if params.get("customer"):
            update_params.update({"CustomerUser": params.get("customer")})
        if params.get("oTRSArticle"):
            new_article = pyotrs.Article(params.get("oTRSArticle"))
            update_params.update(article=new_article)
        dynamic_fields_parameter = params.get("dynamicField")
        if dynamic_fields_parameter:
            logger.debug('PARAMS {0}'.format(dynamic_fields_parameter))
            data_fields = []
            for item in dynamic_fields_parameter:
                logger.debug('ITEM {0}'.format(str(item)))
                name = item['Name']
                value = item['Value']
                data_fields.append(pyotrs.DynamicField(str(name), str(value)))
            logger.debug('dFields {0}'.format(str(data_fields)))
            update_params.update(dynamic_fields=data_fields)
        ticket_info = client.ticket_update(ticket_id, **update_params)

        return {"ticket_metadata": ticket_info}
    except ConnectorError as e:
        raise e
    except Exception as e:
        error_message = "Error updating ticket {0}. Error message as follows:\n{1}".format(ticket_id, str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def get_ticket(config, params):
    ticket_id = params.get("ticket_id")
    try:
        client = _create_client(config)
        ticket = client.ticket_get_by_id(ticket_id, articles=True, attachments=False, dynamic_fields=True)
        return {"ticket": ticket.to_dct()}
    except ConnectorError as e:
        raise e
    except Exception as e:
        error_message = "Error fetching OTRS ticket {0}. Error message as follows:\n{1}".format(ticket_id, str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def search_tickets(config, params):
    try:
        client = _create_client(config)
        states = params.get('state')
        title = params.get('title')
        ticket_type = params.get('tickettype')
        logger.debug('state {0}'.format(str(states)))
        logger.debug('Ticket Type {0}'.format(str(ticket_type)))
        ticket_last_change_time_older_minutes=str(params.get('timeSpanMinutes'))

        if states and ticket_type and title:
          matching_tickets = client.ticket_search(Title=title,States=states,Types=ticket_type)
          return {"count": len(matching_tickets),"matches": matching_tickets}

        if ticket_last_change_time_older_minutes  and title:
          matching_tickets = client.ticket_search(Title=title,TicketLastChangeTimeOlderMinutes=ticket_last_change_time_older_minutes,States=states,Types=ticket_type)
          return {"count": len(matching_tickets),"matches": matching_tickets}


        if ticket_last_change_time_older_minutes :
          matching_tickets = client.ticket_search(TicketLastChangeTimeOlderMinutes=ticket_last_change_time_older_minutes,States=states,Types=ticket_type)
          return {"count": len(matching_tickets), "matches": matching_tickets}

        if states and ticket_type:
          matching_tickets = client.ticket_search(States=states, Types=ticket_type)
          return {"count": len(matching_tickets),"matches": matching_tickets}

        if states:
          matching_tickets = client.ticket_search(States=states, Types=ticket_type)
          return {"count": len(matching_tickets),"matches": matching_tickets}

        if title:
          matching_tickets = client.ticket_search(Title=title,States=states)
          return {"count": len(matching_tickets),"matches": matching_tickets}

        if ticket_last_change_time_older_minutes  and title:
          matching_tickets = client.ticket_search(Title=title,TicketLastChangeTimeOlderMinutes=ticket_last_change_time_older_minutes,States=states,Types=ticket_type)
          return {"count": len(matching_tickets),"matches": matching_tickets}

        if ticket_last_change_time_older_minutes :
          matching_tickets = client.ticket_search(TicketLastChangeTimeOlderMinutes=ticket_last_change_time_older_minutes,States=states,Types=ticket_type)
          return {"count": len(matching_tickets), "matches": matching_tickets}

    except ConnectorError as e:
        raise e
    except Exception as e:
        error_message = "Error performing ticket search. Error message as follows:\n{0}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def check_health(config):
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
