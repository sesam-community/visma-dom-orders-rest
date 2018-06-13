from unittest import TestCase

from service.visma_dom_service import build_api_request_url


class TestBuild_api_request_url(TestCase):
    def test_build_api_request_url(self):
        self.assertEqual(build_api_request_url('https://webappsapistage.azure-api.net',
                                               'distributedordermanager-test/stores/{id}/orders', 1210, {}),
                         'https://webappsapistage.azure-api.net/distributedordermanager-test/stores/1210/orders')
        self.assertEqual(build_api_request_url('https://webappsapistage.azure-api.net',
                                               'distributedordermanager-test/stores/{id}/orders', 1210, {'take': 10}),
                         'https://webappsapistage.azure-api.net/distributedordermanager-test/stores/1210/orders?take=10')
