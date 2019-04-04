"""Micro service for getting data from Visma Distributed Order Manager REST service"""

import os
import logging
import json
from utils import str_to_bool, ts_to_date

import requests

from flask import Flask, request, Response, abort

APP = Flask(__name__)

LOG_LEVEL = os.environ.get('LOG_LEVEL', "INFO")

API_PATH = os.environ.get('API_BASE_PATH')

CONVERT_TS_TO_DATE_STR = str_to_bool(os.environ.get('CONVERT_TS_TO_DATE_STR', 'true'))

if not API_PATH:
    logging.error("API_PATH required")
    exit(1)

# at least Ocp-Apim-Subscription-Key header with API access key must be provided
HEADERS = json.loads(os.environ.get("HEADERS", '{}'))

if not HEADERS.get('Ocp-Apim-Subscription-Key'):
    logging.error("Subscription key not found")
    exit(1)

PORT = os.environ.get('PORT', 5001)


@APP.route('/', methods=['GET'])
def process_request():
    """Micro service end point"""
    logging.debug("Serving request from %s", request.remote_addr)

    return Response(process(HEADERS, request.args), mimetype='application/json')


def process(headers, req_args):
    """processes API call
    """
    yield "["
    first = True

    since = req_args.get('since')
    url = build_api_request_url(API_PATH, since)
    logging.debug("Send request to %s", url)
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        abort(response.status_code, response.text)

    result = response.json()

    for item in result:
        if not first:
            yield ","
        else:
            first = False

        if CONVERT_TS_TO_DATE_STR:
            if item.get('orderChangedDate'):
                item["_updated"] = ts_to_date(item["orderChangedDate"])
            if item.get('collectEndTime'):
                item['collectEndTime'] = ts_to_date(item["collectEndTime"])
            if item.get('collectStartTime'):
                item['collectStartTime'] = ts_to_date(item["collectStartTime"])
            if item.get('orderChangedDate'):
                item['orderChangedDate'] = ts_to_date(item["orderChangedDate"])
            if item.get('orderCollectedDate'):
                item['orderCollectedDate'] = ts_to_date(item["orderCollectedDate"])
            if item.get('orderConfirmationDeadline'):
                item['orderConfirmationDeadline'] = ts_to_date(item["orderConfirmationDeadline"])
            if item.get('orderPlacedDate'):
                item['orderPlacedDate'] = ts_to_date(item["orderPlacedDate"])
        yield json.dumps(item)
    yield "]"


def build_api_request_url(api_path, since=None):
    """builds URL for API request"""
    payload = ''

    if since:
        payload += '?fromDate=' + since
    return api_path + payload


if __name__ == '__main__':
    logging.basicConfig(level=logging.getLevelName(LOG_LEVEL))

    IS_DEBUG_ENABLED = True if logging.getLogger().isEnabledFor(logging.DEBUG) else False

    if IS_DEBUG_ENABLED:
        APP.run(debug=IS_DEBUG_ENABLED, host='0.0.0.0', port=PORT)
    else:
        import cherrypy

        cherrypy.tree.graft(APP, '/')
        cherrypy.config.update({
            'environment': 'production',
            'engine.autoreload_on': True,
            'log.screen': True,
            'server.socket_port': PORT,
            'server.socket_host': '0.0.0.0',
            'server.thread_pool': 10,
            'server.max_request_body_size': 0
        })

        cherrypy.engine.start()
        cherrypy.engine.block()

