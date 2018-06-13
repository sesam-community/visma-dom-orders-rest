"""Micro service for getting data from Visma Distributed Order Manager REST service"""

import os
import logging
import json
from urllib.parse import urlencode

import requests
from flask import Flask, request, Response, abort

APP = Flask(__name__)

LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.INFO)

API_BASE_PATH = os.environ.get('API_BASE_PATH', 'https://webappsapistage.azure-api.net/')
API_PATH = os.environ.get('API_PATH', 'distributedordermanager-test/stores/{id}/orders')
ID_ARR = os.environ.get('ID_ARR', '').split(',')

# at least Ocp-Apim-Subscription-Key header with API access key must be provided
HEADERS = json.loads(
    os.environ.get("HEADERS", '{"Ocp-Apim-Subscription-Key":""}'))
PORT = os.environ.get('PORT', 5001)


@APP.route('/', methods=['GET'])
def process_request():
    """Micro service end point"""
    logging.debug("Serving request from %s", request.remote_addr)
    data = []
    for entity_id in ID_ARR:
        logging.debug("Processing entiity_id=%s", entity_id)
        data += process_entity(entity_id, HEADERS)
    return Response(json.dumps(data), mimetype='application/json')


def process_entity(entity_id, headers):
    """processes API call for given entity_id
    entity_id is a part of URL
    """
    data_to_return = []
    offset = 0
    items_to_take = 20
    while True:
        url = build_api_request_url(API_BASE_PATH, API_PATH, entity_id,
                                    {'skip': offset, 'take': items_to_take})
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            abort(500, "Remote API returned non 200 code")
        result = response.json()
        offset += items_to_take
        data_to_return += result
        if len(result) < items_to_take:
            break
    return data_to_return


def build_api_request_url(api_base_path, api_path, entity_id, query_dict=None):
    """builds URL for API request"""
    payload = ''

    if not api_base_path.endswith("/"):
        api_base_path = api_base_path + "/"

    if query_dict:
        payload = '?' + urlencode(query_dict)
    return (api_base_path + api_path + payload).format(id=entity_id)


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    IS_DEBUG_ENABLED = True if logging.getLogger().isEnabledFor(logging.DEBUG) else False
    APP.run(debug=IS_DEBUG_ENABLED, host='0.0.0.0', port=PORT)
