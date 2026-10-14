from playwright.sync_api import expect
import pytest

from tests.messages import Messages

def test_user_can_register_successfully(
    register_page,
    user_data
):
    """
    Verify that a new user can successfully register through the UI.

    The test uses unique test data provided by the `user_data` fixture
    to avoid conflicts with users created by previous test runs.

    The registration form is completed with a valid name, email address,
    and password. After submitting the form, the test verifies that
    the expected success message is displayed to the user.

    This test covers the main registration flow from the UI through
    the frontend and API to the database.
    """

    register_page.open()

    register_page.register_user(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"]
    )

    expect(register_page.get_message()).to_have_text(
        "Registration successful!"
    )

@pytest.mark.parametrize(
    "name, email, password, expected_message",
    [
        ("", "test@test.pl", "secret123", Messages.NAME_REQUIRED),
        ("Test User", "", "secret123", Messages.EMAIL_REQUIRED),
        ("Test User", "test@test.pl", "", Messages.PASSWORD_REQUIRED),
    ]
)
def test_user_cannot_register_with_empty_required_field(
    register_page,
    name,
    email,
    password,
    expected_message
):
    """
    Verify that registration is prevented when a required field is empty.

    The test checks frontend validation for the name, email, and password
    fields. Each test case provides valid data for the remaining fields
    and leaves one required field empty.

    The test verifies that the appropriate validation message is displayed
    to the user.
    """

    register_page.open()

    register_page.register_user(
        name=name,
        email=email,
        password=password
    )

    expect(register_page.get_message()).to_have_text(expected_message)

def test_user_cannot_register_with_existing_email(
    register_page,
    api_client,
    user_data
):
    """
    Verify that a user cannot register with an email address
    that is already registered.

    An existing user is created through the API as test data.
    The test then attempts to register another user through the UI
    using the same email address.

    The test verifies that the expected duplicate-email error message
    is displayed to the user.
    """

    # Arrange - create an existing user through the API
    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    # Act - try to register through the UI with the same email
    register_page.open()

    register_page.register_user(
        name="Another User",
        email=user_data["email"],
        password="anotherpassword123"
    )

    # Assert
    expect(register_page.get_message()).to_have_text(
        Messages.EMAIL_ALREADY_EXISTS
    )

def test_user_cannot_register_with_too_short_password(register_page):
    register_page.open()

    register_page.register_user(
        name="Test User",
        email="test@test.pl",
        password="1234567",
    )

    expect(register_page.get_message()).to_have_text(Messages.PASSWORD_TOO_SHORT)

def test_user_cannot_register_with_too_short_name(register_page):
    register_page.open()
    register_page.register_user(
        name="A",
        email="test@test.pl",
        password="secret123",
    )

    expect(register_page.get_message()).to_have_text(Messages.NAME_TOO_SHORT)


def test_user_sees_error_message_when_server_returns_500(
    register_page,
    user_data
):
    """
    Verify that the user sees an error message when the server
    returns HTTP 500 during registration.

    The registration request is intercepted and answered with
    HTTP 500 and a non-JSON body, as returned by a failing server.

    The test verifies that a generic server error message is displayed
    to the user.
    """

    register_page.page.route(
        "**/users",
        lambda route: route.fulfill(
            status=500,
            content_type="text/plain",
            body="Internal Server Error"
        )
    )

    register_page.open()

    register_page.register_user(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"]
    )

    expect(register_page.get_message()).to_have_text(Messages.SERVER_ERROR)
    expect(register_page.get_message()).to_have_class("error-message")


def test_user_sees_error_message_when_connection_fails(
    register_page,
    user_data
):
    """
    Verify that the user sees an error message when the registration
    request cannot reach the server.

    The registration request is intercepted and aborted to simulate
    a network failure.

    The test verifies that a connection error message is displayed
    to the user.
    """

    register_page.page.route(
        "**/users",
        lambda route: route.abort("connectionrefused")
    )

    register_page.open()

    register_page.register_user(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"]
    )

    expect(register_page.get_message()).to_have_text(Messages.CONNECTION_ERROR)
    expect(register_page.get_message()).to_have_class("error-message")
