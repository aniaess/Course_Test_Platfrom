import pytest
import uuid

from tests.messages import Messages


def test_create_user(api_client, user_data):
    """
    Verify that a new user can be successfully created through the API.

    The test sends valid user data to the POST /users endpoint and
    verifies that the API returns HTTP 201 Created.

    The response is also checked to ensure that the created user's
    name and email match the data sent in the request.
    """

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["name"] == user_data["name"]
    assert response_data["email"] == user_data["email"]


def test_create_user_with_duplicate_email_returns_409(
    api_client,
    user_data
):
    """
    Verify that the API rejects a user registration when the email
    address is already registered.

    The test first creates a user with valid data and then attempts
    to create another user using the same email address.

    The test verifies that the API returns HTTP 409 Conflict and
    provides the expected duplicate-email error message.
    """

    first_response = api_client.post(
        "/users",
        json=user_data
    )

    assert first_response.status_code == 201

    second_response = api_client.post(
        "/users",
        json=user_data
    )

    assert second_response.status_code == 409

    response_data = second_response.json()

    assert response_data["detail"] == Messages.EMAIL_ALREADY_EXISTS


@pytest.mark.parametrize(
    "user_data, missing_field",
    [
        (
            {"email": "test@test.pl", "password": "secret123"},
            "name"
        ),
        (
            {"name": "Test User", "password": "secret123"},
            "email"
        ),
        (
            {"name": "Test User", "email": "test@test.pl"},
            "password"
        ),
    ]
)
def test_create_user_without_required_field_returns_422(
    api_client,
    user_data,
    missing_field
):
    """
    Verify that the API rejects a user creation request when a required
    field is missing.

    The test sends three different requests, each missing one required
    field: name, email, or password.

    The test verifies that the API returns HTTP 422 Unprocessable Entity
    and identifies the missing field in the validation response.
    """

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 422

    response_data = response.json()

    assert response_data["detail"][0]["loc"] == [
        "body",
        missing_field
    ]


@pytest.mark.parametrize(
    "user_data, invalid_field",
    [
        (
            {
                "name": 123,
                "email": "test@test.pl",
                "password": "secret123"
            },
            "name"
        ),
        (
            {
                "name": "Test User",
                "email": 123,
                "password": "secret123"
            },
            "email"
        ),
        (
            {
                "name": "Test User",
                "email": "test@test.pl",
                "password": 123
            },
            "password"
        ),
    ]
)
def test_create_user_with_invalid_data_type_returns_422(
    api_client,
    user_data,
    invalid_field
):
    """
    Verify that the API rejects a user creation request when a field
    contains an invalid data type.

    Each test case sends a request where one user field contains an
    invalid data type while the remaining fields contain valid data.

    The test verifies that the API returns HTTP 422 Unprocessable Entity
    and identifies the field with the invalid data type.
    """

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 422

    response_data = response.json()

    assert response_data["detail"][0]["loc"] == [
        "body",
        invalid_field
    ]


@pytest.mark.parametrize(
    "name, expected_status_code",
    [
        ("A", 422),        # 1 character - below minimum
        ("AB", 201),       # 2 characters - minimum
        ("A" * 100, 201),  # 100 characters - maximum
        ("A" * 101, 422),  # 101 characters - above maximum
    ]
)
def test_create_user_with_name_length_boundary(
    api_client,
    name,
    expected_status_code
):
    """
    Verify that the API correctly validates the length of the user's name.

    The test checks values below, at, and above the allowed name length
    boundaries. The minimum allowed length is 2 characters and the maximum
    allowed length is 100 characters.

    The test verifies that values within the allowed range are accepted
    with HTTP 201 Created, while values outside the range are rejected
    with HTTP 422 Unprocessable Entity.
    """

    user_data = {
        "name": name,
        "email": f"test-{uuid.uuid4()}@test.pl",
        "password": "secret123"
    }

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 422:
        response_data = response.json()

        assert response_data["detail"][0]["loc"] == [
            "body",
            "name"
        ]


@pytest.mark.parametrize(
    "email",
    [
        "test",
        "test@",
        "@test.pl",
        "test@test",
        "test.pl",
        "test@@test.pl",
    ]
)
def test_create_user_with_invalid_email_returns_422(
    api_client,
    email
):
    """
    Verify that the API rejects a user creation request when the email
    address has an invalid format.

    The test sends different invalid email formats while providing
    valid values for the remaining user fields.

    The test verifies that the API returns HTTP 422 Unprocessable Entity
    and identifies the email field in the validation response.
    """

    user_data = {
        "name": "Test User",
        "email": email,
        "password": "secret123"
    }

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 422

    response_data = response.json()

    assert response_data["detail"][0]["loc"] == [
        "body",
        "email"
    ]


@pytest.mark.parametrize(
    "password, expected_status_code",
    [
        ("1234567", 422),
        ("12345678", 201),
        ("A" * 100, 201),
    ]
)
def test_create_user_with_password_length_boundary(
    api_client,
    password,
    expected_status_code
):
    """
    Verify that the API correctly validates the minimum length of a
    user's password.

    The test checks password values below and at the minimum allowed
    length, as well as longer valid passwords.

    The minimum password length is 8 characters. Passwords shorter
    than the minimum are rejected with HTTP 422, while valid passwords
    are accepted with HTTP 201 Created.
    """

    user_data = {
        "name": "Test User",
        "email" : f"test-{uuid.uuid4()}@test.pl",
        "password": password
    }

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 422:
        response_data = response.json()

        assert response_data["detail"][0]["loc"] == [
            "body",
            "password"
        ]


def test_create_user_response_does_not_expose_password(
    api_client,
    user_data
):
    """
    Verify that the API response does not expose the user's password
    or its hash.

    The test creates a user through the API and checks the response body.

    The test verifies that the response contains only the public user
    fields (id, name, email), that no value equals the password sent
    in the request, and that no value looks like an Argon2 hash.
    """

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    response_data = response.json()

    assert set(response_data.keys()) == {"id", "name", "email"}

    for value in response_data.values():
        assert value != user_data["password"]

        if isinstance(value, str):
            assert not value.startswith("$argon2")
