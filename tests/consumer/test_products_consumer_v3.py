"""pact test for product service client"""

import logging
import os

import pytest
from pact import PactV3
from pact.ffi.native_mock_server import MockServerStatus
from pact.matchers_v3 import Like, Format
from src.consumer import ProductConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
print(Format().__dict__)

PACT_MOCK_HOST = '127.0.0.1'
PACT_MOCK_PORT = 8888
PACT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def consumer():
    return ProductConsumer(
        'http://{host}:{port}'
        .format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT)
    )


@pytest.fixture(scope='session')
def pact(request):
    pact = PactV3(
        'pactflow-example-consumer-python-v3',
        'pactflow-example-provider-python-v3',
        hostname=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir="./pacts",
    )

    return pact

def test_get_product(pact: PactV3, consumer):
    expected = {
        'id': "27",
        'name': 'Margharita',
        'type': 'Pizza'
    }

    (pact
     .new_http_interaction('interaction')
     .given('a product with ID 10 exists')
     .upon_receiving('a request to get a product')
     .with_request('GET', '/product/10')
     .will_respond_with(200, body=Like(expected), headers=[{"name": 'content-type', "value": 'application/json'}]))

    with pact:
        pact.start_service()
        user = consumer.get_product('10')
        assert user.name == 'Margharita'
        result = pact.verify()
        assert MockServerStatus(result.return_code) == MockServerStatus.SUCCESS
