from unittest import mock

import pytest
from sage_utils.amqp.extension import AmqpExtension
from sage_utils.amqp.workers import BaseRegisterWorker

from tests.fixtures import Application, FakeConfig, FakeRegisterMicroserviceWorker


REQUEST_QUEUE = FakeRegisterMicroserviceWorker.QUEUE_NAME
REQUEST_EXCHANGE = FakeRegisterMicroserviceWorker.REQUEST_EXCHANGE_NAME
RESPONSE_EXCHANGE_NAME = FakeRegisterMicroserviceWorker.RESPONSE_EXCHANGE_NAME


def valid_microservice_data(_app):
    return {'name': 'microservice', 'version': '1.0.0'}


def invalid_microservice_data(_app):
    return {}


def test_default_implementation_raises_an_error_when_getting_data():
    with pytest.raises(NotImplementedError):
        app = Application(config=FakeConfig())
        instance = BaseRegisterWorker(app)
        instance.get_microservice_data(app)


@pytest.mark.asyncio
async def test_microservice_has_been_registered_successfully(event_loop):
    app = Application(config=FakeConfig(), loop=event_loop)
    register_worker = FakeRegisterMicroserviceWorker(app)
    extension = AmqpExtension(app)
    extension.register_worker(register_worker)

    await extension.init(event_loop)

    instance = BaseRegisterWorker(app)
    instance.REQUEST_QUEUE_NAME = REQUEST_QUEUE
    instance.REQUEST_EXCHANGE_NAME = REQUEST_EXCHANGE
    instance.RESPONSE_EXCHANGE_NAME = RESPONSE_EXCHANGE_NAME

    with mock.patch(
        target='sage_utils.amqp.workers.BaseRegisterWorker.get_microservice_data',
        side_effect=valid_microservice_data
    ):
        result = await instance.run()
        assert result is None

    await extension.deinit(event_loop)


@pytest.mark.asyncio
async def test_register_worker_raises_an_error_with_invalid_response(event_loop):
    app = Application(config=FakeConfig(), loop=event_loop)
    register_worker = FakeRegisterMicroserviceWorker(app)
    extension = AmqpExtension(app)
    extension.register_worker(register_worker)

    await extension.init(event_loop)

    instance = BaseRegisterWorker(app)
    instance.REQUEST_QUEUE_NAME = REQUEST_QUEUE
    instance.REQUEST_EXCHANGE_NAME = REQUEST_EXCHANGE
    instance.RESPONSE_EXCHANGE_NAME = RESPONSE_EXCHANGE_NAME
    instance.RETRY_TIMEOUT = 0.1
    instance.MAX_RETRIES = 1

    with mock.patch(
        target='sage_utils.amqp.workers.BaseRegisterWorker.get_microservice_data',
        side_effect=invalid_microservice_data
    ):
        with pytest.raises(ConnectionError):
            await instance.run()

    await extension.deinit(event_loop)


@pytest.mark.asyncio
async def test_register_worker_raises_an_error(event_loop):
    app = Application(config=FakeConfig(), loop=event_loop)
    register_worker = FakeRegisterMicroserviceWorker(app)
    extension = AmqpExtension(app)
    extension.register_worker(register_worker)

    await extension.init(event_loop)

    instance = BaseRegisterWorker(app)
    instance.REQUEST_QUEUE_NAME = 'invalid.queue.name'
    instance.REQUEST_EXCHANGE_NAME = 'some.request.exchange'
    instance.RESPONSE_EXCHANGE_NAME = 'some.response.exchange'
    instance.RETRY_TIMEOUT = 0.1
    instance.MAX_RETRIES = 1

    with mock.patch(
        target='sage_utils.amqp.workers.BaseRegisterWorker.get_microservice_data',
        side_effect=valid_microservice_data
    ):
        with pytest.raises(ConnectionError):
            await instance.run()

    await extension.deinit(event_loop)
