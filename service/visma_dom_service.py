"""Micro service for getting data from Visma Distributed Order Manager REST service"""

import os
import logging
import json
from urllib.parse import urlencode

import requests
from flask import Flask, request, Response, abort

APP = Flask(__name__)

LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.DEBUG)

API_PATH = os.environ.get('API_BASE_PATH')

if not API_PATH:
    logging.error("API_PATH required")
    exit(1)

# at least Ocp-Apim-Subscription-Key header with API access key must be provided
HEADERS = json.loads(os.environ.get("HEADERS", '{}'))
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
    offset = 0
    items_to_take = 20
    first = True
    while True:
        since = req_args.get('since')
        url = build_api_request_url(API_PATH, {'skip': offset, 'take': items_to_take}, since)
        logging.debug("Send request to %s", url)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            abort(response.status_code, response.text)
        result = response.json()
        offset += items_to_take

        for item in result:
            if not first:
                yield ","
            else:
                first = False
            yield json.dumps(item)

        if len(result) < items_to_take:
            break
    yield "]"


def build_api_request_url(api_path, query_dict=None, since=None):
    """builds URL for API request"""
    payload = ''
    if query_dict:
        payload = '?' + urlencode(query_dict)

    if since is not None:
        payload += '&fromDate=' + since
    return api_path + payload


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    IS_DEBUG_ENABLED = True if logging.getLogger().isEnabledFor(logging.DEBUG) else False
    APP.run(debug=IS_DEBUG_ENABLED, host='0.0.0.0', port=PORT)
