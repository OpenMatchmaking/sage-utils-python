import asyncio
import os
import json

from sage_utils.amqp.base import AmqpWorker
from sage_utils.constants import VALIDATION_ERROR
from sage_utils.wrappers import Response


class FakeConfig(object):

    def get(self, key, default=None):
        return os.environ.get(key, default)


class Application(object):

    def __init__(self, config=None, loop=None):
        super(Application, self).__init__()
        self.config = config
        self.loop = loop or asyncio.get_event_loop()


class BaseWorker(AmqpWorker):
    QUEUE_NAME = 'process-request'
    REQUEST_EXCHANGE_NAME = 'amq.direct'
    RESPONSE_EXCHANGE_NAME = 'amq.direct'
    CONTENT_TYPE = 'application/json'

    def generate_response(self, data):
        raise NotImplementedError('`generate_response(data)` method must be implemented.')

    async def process_request(self, channel, body, envelope, properties):
        response = self.generate_response(body)
        await channel.publish(
            json.dumps(response.data),
            exchange_name=self.RESPONSE_EXCHANGE_NAME,
            routing_key=properties.reply_to,
            properties={
                'content_type': self.CONTENT_TYPE,
                'delivery_mode': 2,
                'correlation_id': properties.correlation_id
            }
        )

        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    async def consume_callback(self, channel, body, envelope, properties):
        self.app.loop.create_task(self.process_request(channel, body, envelope, properties))

    async def run(self, *args, **kwargs):
        _transport, protocol = await self.connect()

        channel = await protocol.channel()
        await channel.queue_declare(
            queue_name=self.QUEUE_NAME,
            durable=True,
            passive=False,
            auto_delete=False
        )
        await channel.queue_bind(
            queue_name=self.QUEUE_NAME,
            exchange_name=self.REQUEST_EXCHANGE_NAME,
            routing_key=self.QUEUE_NAME
        )
        await channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)
        await channel.basic_consume(self.consume_callback, queue_name=self.QUEUE_NAME)


class FakeRegisterMicroserviceWorker(BaseWorker):
    QUEUE_NAME = 'microservice.register'
    ERROR_DESCRIPTION = "Name and version must be specified."

    def generate_response(self, raw_data):
        data = json.loads(raw_data.strip())

        if 'name' not in data.keys() and 'version' not in data.keys():
            return Response.from_error(VALIDATION_ERROR, self.ERROR_DESCRIPTION)
        return Response.with_content("OK")
