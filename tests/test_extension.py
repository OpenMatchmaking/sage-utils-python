import pytest
from sage_utils.extension import BaseExtension


from tests.fixtures import Application, FakeConfig as BaseFakeConfig


class FakeConfig(BaseFakeConfig):
    key = 'value'


class CustomExtension(BaseExtension):
    extension_name = 'ext'
    app_attribute = 'ext'


def test_constructor_with_init():
    app = Application()
    extension = CustomExtension(app)

    assert 'extensions' in app.__dict__
    assert isinstance(app.extensions, dict)
    assert len(app.extensions.keys()) == 1
    assert extension.extension_name in app.extensions.keys()
    assert app.extensions[extension.extension_name] == extension


def test_get_from_app_config_returns_value():
    app = Application(config=FakeConfig())
    extension = CustomExtension(app)

    assert extension.get_from_app_config(app, 'key') == 'value'


def test_get_from_app_config_returns_none():
    app = Application(config=FakeConfig())
    extension = CustomExtension(app)

    assert extension.get_from_app_config(app, 'UNKNOWN_KEY') is None


@pytest.mark.asyncio
async def test_init_returns_none_by_default(event_loop):
    app = Application()
    extension = CustomExtension(app)

    result = await extension.init(event_loop)
    assert result is None


@pytest.mark.asyncio
async def test_deinit_returns_none_by_default(event_loop):
    app = Application()
    extension = CustomExtension(app)

    result = await extension.deinit(event_loop)
    assert result is None
