import pytest
from sage_utils.amqp.clients import RpcAmqpClient
from sage_utils.amqp.extension import AmqpExtension
from sage_utils.constants import VALIDATION_ERROR
from sage_utils.wrappers import Response

from tests.fixtures import Application, FakeConfig, FakeRegisterMicroserviceWorker


REQUEST_QUEUE = FakeRegisterMicroserviceWorker.QUEUE_NAME
REQUEST_EXCHANGE = FakeRegisterMicroserviceWorker.REQUEST_EXCHANGE_NAME
RESPONSE_EXCHANGE_NAME = FakeRegisterMicroserviceWorker.RESPONSE_EXCHANGE_NAME
VALIDATION_ERROR_DECR = FakeRegisterMicroserviceWorker.ERROR_DESCRIPTION


@pytest.mark.asyncio
async def test_rpc_amqp_client_returns_ok(event_loop):
    app = Application(config=FakeConfig(), loop=event_loop)
    register_worker = FakeRegisterMicroserviceWorker(app)
    extension = AmqpExtension(app)
    extension.register_worker(register_worker)

    await extension.init(event_loop)

    client = RpcAmqpClient(
        app=app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE_NAME
    )
    response = await client.send(payload={'name': 'microservice', 'version': '1.0.0'})

    assert Response.CONTENT_FIELD_NAME in response.keys()
    assert response[Response.CONTENT_FIELD_NAME] == 'OK'

    assert Response.EVENT_FIELD_NAME in response.keys()
    assert response[Response.EVENT_FIELD_NAME] is None

    await extension.deinit(event_loop)


@pytest.mark.asyncio
async def test_rpc_amqp_client_returns_ok_with_custom_event_loop(event_loop):
    app = Application(config=FakeConfig(), loop=event_loop)
    register_worker = FakeRegisterMicroserviceWorker(app)
    extension = AmqpExtension(app)
    extension.register_worker(register_worker)

    await extension.init(event_loop)

    client = RpcAmqpClient(
        app=app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE_NAME,
        loop=event_loop
    )
    response = await client.send(payload={'name': 'microservice', 'version': '1.0.0'})

    assert Response.CONTENT_FIELD_NAME in response.keys()
    assert response[Response.CONTENT_FIELD_NAME] == 'OK'

    assert Response.EVENT_FIELD_NAME in response.keys()
    assert response[Response.EVENT_FIELD_NAME] is None

    await extension.deinit(event_loop)


@pytest.mark.asyncio
async def test_rpc_amqp_client_returns_an_error(event_loop):
    app = Application(config=FakeConfig(), loop=event_loop)
    register_worker = FakeRegisterMicroserviceWorker(app)
    extension = AmqpExtension(app)
    extension.register_worker(register_worker)

    await extension.init(event_loop)

    client = RpcAmqpClient(
        app=app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE_NAME
    )
    response = await client.send(payload={})

    assert Response.ERROR_FIELD_NAME in response.keys()
    assert Response.ERROR_TYPE_FIELD_NAME in response[Response.ERROR_FIELD_NAME].keys()
    assert response[Response.ERROR_FIELD_NAME][Response.ERROR_TYPE_FIELD_NAME] == VALIDATION_ERROR  # NOQA

    assert Response.ERROR_DETAILS_FIELD_NAME in response[Response.ERROR_FIELD_NAME].keys()
    assert response[Response.ERROR_FIELD_NAME][Response.ERROR_DETAILS_FIELD_NAME] == VALIDATION_ERROR_DECR  # NOQA

    assert Response.EVENT_FIELD_NAME in response.keys()
    assert response[Response.EVENT_FIELD_NAME] is None

    await extension.deinit(event_loop)
