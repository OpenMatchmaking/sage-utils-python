import asyncio
import os

import pytest
from sage_utils.amqp.extension import AmqpExtension
from sage_utils.amqp.base import AmqpWorker


class FakeConfig(object):

    def get(self, key, default=None):
        return os.environ.get(key, default)


class Application(object):

    def __init__(self, config=None):
        super(Application, self).__init__()
        self.config = config


class CustomWorker(AmqpWorker):

    async def run(self, *args, **kwargs):
        await self.connect()


@pytest.mark.asyncio
async def test_extension_without_workers(event_loop):
    app = Application()
    extension = AmqpExtension(app)

    await extension.init(event_loop)
    assert 'extensions' in app.__dict__
    assert isinstance(app.extensions, dict)
    assert len(app.extensions.keys()) == 1
    assert extension.extension_name in app.extensions.keys()
    assert app.extensions[extension.extension_name] == extension
    assert len(extension.active_tasks) == 0

    await asyncio.sleep(0.1)

    await extension.deinit(event_loop)
    assert 'extensions' in app.__dict__
    assert extension.extension_name not in app.extensions.keys()
    assert getattr(app, AmqpExtension.app_attribute) is None
    assert len(extension.active_tasks) == 0


@pytest.mark.asyncio
async def test_extension_init_with_workers(event_loop):
    app = Application(config=FakeConfig())
    amqp_worker = CustomWorker(app)
    extension = AmqpExtension(app)
    extension.register_worker(amqp_worker)

    await extension.init(event_loop)
    assert 'extensions' in app.__dict__
    assert isinstance(app.extensions, dict)
    assert len(app.extensions.keys()) == 1
    assert extension.extension_name in app.extensions.keys()
    assert app.extensions[extension.extension_name] == extension
    assert len(extension.active_tasks) == 1

    await asyncio.sleep(0.1)

    await extension.deinit(event_loop)
    assert 'extensions' in app.__dict__
    assert extension.extension_name not in app.extensions.keys()
    assert getattr(app, AmqpExtension.app_attribute) is None
    assert len(extension.active_tasks) == 1
