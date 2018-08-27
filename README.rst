====================
visma-dom-orders-rest
====================

Microservice for fetching orders data from Visma DOM REST API

.. image:: https://travis-ci.org/timurgen/visma-dom-orders-rest.svg?branch=master
    :target: https://travis-ci.org/timurgen/visma-dom-orders-rest

::
example config 
::

    
    {
  "_id": "visma-dom",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "API_BASE_PATH": "$ENV(avinor-visma-dom-api-url)",
      "HEADERS": {
        "Ocp-Apim-Subscription-Key": "$SECRET(avinor-visma-dom-api-key)"
      },
      "LOG_LEVEL": "DEBUG"
    },
    "image": "ohuenno/visma-dom",
    "port": 5001
  }
 },{
      "_id": "visma-dom-orders",
      "type": "pipe",
      "source": {
        "type": "json",
        "system": "visma-dom-orders-s",
        "url": ""
      },
      "transform": {
        "type": "dtl",
        "rules": {
          "default": [
            ["add", "_id", "_S.orderId"],
            ["copy", "*"]
          ]
        }
      },
      "pump": {
        "schedule_interval": 3600
      }
    }


