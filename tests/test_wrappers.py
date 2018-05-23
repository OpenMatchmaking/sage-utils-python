import pytest
from sage_utils import constants
from sage_utils.wrappers import Response


@pytest.mark.parametrize("error_type, message, event_name", [
    (constants.AUTHORIZATION_ERROR, "Invalid password.", "auth-response"),
    (constants.HEADER_ERROR, "Missing header.", "header-response"),
    (constants.NOT_FOUND_ERROR, "Invalid password.", "not-found-response"),
    (constants.TOKEN_ERROR, "Token has expired.", "token-response"),
    (constants.VALIDATION_ERROR, "Validation error.", "validation-response"),
])
def test_from_error_class_method(error_type, message, event_name):
    response = Response.from_error(error_type, message, event_name)

    assert isinstance(response, Response)
    assert isinstance(response.data, dict)

    assert Response.EVENT_FIELD_NAME in response.data.keys()
    assert response.data[Response.EVENT_FIELD_NAME] == event_name

    assert Response.ERROR_FIELD_NAME in response.data.keys()
    assert Response.ERROR_TYPE_FIELD_NAME in response.data[Response.ERROR_FIELD_NAME].keys()
    assert response.data[Response.ERROR_FIELD_NAME][Response.ERROR_TYPE_FIELD_NAME] == error_type

    assert Response.ERROR_DETAILS_FIELD_NAME in response.data[Response.ERROR_FIELD_NAME].keys()
    assert response.data[Response.ERROR_FIELD_NAME][Response.ERROR_DETAILS_FIELD_NAME] == message


@pytest.mark.parametrize("error_type, message, event_name", [
    (constants.VALIDATION_ERROR, "Missing field", "validation-response"),
])
def test_from_error_with_a_message_without_the_period_in_the_end(error_type, message, event_name):
    response = Response.from_error(error_type, message, event_name)

    assert isinstance(response, Response)
    assert isinstance(response.data, dict)

    assert Response.EVENT_FIELD_NAME in response.data.keys()
    assert response.data[Response.EVENT_FIELD_NAME] == event_name

    assert Response.ERROR_FIELD_NAME in response.data.keys()
    assert Response.ERROR_TYPE_FIELD_NAME in response.data[Response.ERROR_FIELD_NAME].keys()
    assert response.data[Response.ERROR_FIELD_NAME][Response.ERROR_TYPE_FIELD_NAME] == error_type

    assert Response.ERROR_DETAILS_FIELD_NAME in response.data[Response.ERROR_FIELD_NAME].keys()
    assert response.data[Response.ERROR_FIELD_NAME][Response.ERROR_DETAILS_FIELD_NAME].endswith('.')  # NOQA
    assert response.data[Response.ERROR_FIELD_NAME][Response.ERROR_DETAILS_FIELD_NAME] == "{}.".format(message)  # NOQA


@pytest.mark.parametrize("data, event_name", [
    ({'is_valid': True}, "auth-response"),
])
def test_with_content_class_method(data, event_name):
    response = Response.with_content(data, event_name)

    assert isinstance(response, Response)
    assert isinstance(response.data, dict)

    assert Response.CONTENT_FIELD_NAME in response.data.keys()
    assert response.data[Response.CONTENT_FIELD_NAME] == data

    assert Response.EVENT_FIELD_NAME in response.data.keys()
    assert response.data[Response.EVENT_FIELD_NAME] == event_name
