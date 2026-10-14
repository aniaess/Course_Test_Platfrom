import pytest
import uuid

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from psycopg2.errors import NotNullViolation


def test_created_user_is_persisted_in_database(
    api_client,
    db_connection,
    user_data
):
    """
    Verify that a successfully created user is persisted in the database.

    The test creates a user through the API and then queries the database
    to verify that the user's name and email were stored correctly.
    """

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    cursor = db_connection.cursor()

    cursor.execute(
        """
        SELECT name, email
        FROM users
        WHERE email = %s
        """,
        (user_data["email"],)
    )

    user = cursor.fetchone()

    assert user is not None
    assert user[0] == user_data["name"]
    assert user[1] == user_data["email"]

import pytest

from psycopg2.errors import UniqueViolation


def test_user_email_must_be_unique(
    db_connection,
    user_data
):
    """
    Verify that the database does not allow two users with the same
    email address.

    The test inserts a user into the database and then attempts to
    insert another user using the same email address.

    The test verifies that PostgreSQL raises a UniqueViolation error.
    """

    cursor = db_connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """,
        (
            user_data["name"],
            user_data["email"],
            user_data["password"]
        )
    )

    db_connection.commit()

    with pytest.raises(UniqueViolation):
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (
                "Another User",
                user_data["email"],
                "anotherpassword123"
            )
        )

    db_connection.rollback()

@pytest.mark.parametrize(
    "column",
    [
        "name",
        "email",
        "password",
    ]
)
def test_user_required_fields_cannot_be_null(
    db_connection,
    user_data,
    column
):
    """
    Verify that the database does not allow NULL values in required
    user fields.

    The test attempts to insert a user with a NULL value in each
    required field: name, email, or password.

    The test verifies that PostgreSQL raises a NotNullViolation
    for each required field.
    """

    cursor = db_connection.cursor()

    values = {
        "name": user_data["name"],
        "email": user_data["email"],
        "password": user_data["password"],
    }

    values[column] = None

    with pytest.raises(NotNullViolation):
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (
                values["name"],
                values["email"],
                values["password"]
            )
        )

    db_connection.rollback()

def test_users_table_has_expected_columns(db_connection):
    """
    Verify that the users table contains the expected columns and
    data types.

    The test queries PostgreSQL information_schema and verifies that
    the users table contains the required columns with the expected
    data types.
    """

    cursor = db_connection.cursor()

    cursor.execute(
        """
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position
        """
    )

    columns = cursor.fetchall()

    expected_columns = [
        ("id", "integer", None),
        ("name", "character varying", 100),
        ("email", "character varying", 255),
        ("password", "character varying", 255),
    ]

    assert columns == expected_columns


def get_stored_password(db_connection, email):
    """Return the password value stored in the database for the given email."""

    cursor = db_connection.cursor()

    cursor.execute(
        """
        SELECT password
        FROM users
        WHERE email = %s
        """,
        (email,)
    )

    row = cursor.fetchone()

    cursor.close()

    assert row is not None, f"User with email {email} was not found"

    return row[0]


def test_password_is_not_stored_in_plaintext(
    api_client,
    db_connection,
    user_data
):
    """
    Verify that the user's password is not stored in plaintext.

    The test creates a user through the API and then reads the stored
    password value from the database.

    The test verifies that the stored value is different from the
    password sent in the registration request.
    """

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    stored_password = get_stored_password(
        db_connection,
        user_data["email"]
    )

    assert stored_password != user_data["password"]


def test_password_is_stored_as_argon2id_hash(
    api_client,
    db_connection,
    user_data
):
    """
    Verify that the user's password is stored as an Argon2id hash.

    The test creates a user through the API and then reads the stored
    password value from the database.

    The test verifies that the stored value uses the Argon2id PHC string
    format (prefix "$argon2id$") and fits in the password column.
    """

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    stored_password = get_stored_password(
        db_connection,
        user_data["email"]
    )

    assert stored_password.startswith("$argon2id$")
    assert len(stored_password) <= 255


def test_same_password_produces_different_stored_values(
    api_client,
    db_connection,
    user_data
):
    """
    Verify that the same password produces different stored values
    for different users.

    The test creates two users through the API with the same password
    and different email addresses, then reads both stored password
    values from the database.

    The test verifies that the stored values are different, which
    confirms that each password hash uses its own salt.
    """

    second_user_data = {
        "name": "Another User",
        "email": f"playwright-{uuid.uuid4()}@test.pl",
        "password": user_data["password"]
    }

    first_response = api_client.post(
        "/users",
        json=user_data
    )

    assert first_response.status_code == 201

    second_response = api_client.post(
        "/users",
        json=second_user_data
    )

    assert second_response.status_code == 201

    first_stored_password = get_stored_password(
        db_connection,
        user_data["email"]
    )

    second_stored_password = get_stored_password(
        db_connection,
        second_user_data["email"]
    )

    assert first_stored_password != second_stored_password


def test_name_is_stored_without_surrounding_whitespace(
    api_client,
    db_connection,
    user_data
):
    """
    Verify that the name is stored without leading and trailing
    whitespace.

    The test creates a user through the API with a name surrounded
    by spaces and reads the stored name from the database.
    """

    user_data["name"] = "  Test User  "

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    cursor = db_connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM users
        WHERE email = %s
        """,
        (user_data["email"],)
    )

    stored_name = cursor.fetchone()[0]

    cursor.close()

    assert stored_name == "Test User"


def test_password_whitespace_is_preserved(
    api_client,
    db_connection,
    user_data
):
    """
    Verify that leading and trailing whitespace in the password
    is not removed.

    The test creates a user through the API with a password surrounded
    by spaces and reads the stored hash from the database.

    The test verifies that the hash matches the password with spaces
    and does not match the trimmed password.
    """

    password = "  secret123  "
    user_data["password"] = password

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    stored_password = get_stored_password(
        db_connection,
        user_data["email"]
    )

    password_hasher = PasswordHasher()

    assert password_hasher.verify(stored_password, password)

    with pytest.raises(VerifyMismatchError):
        password_hasher.verify(stored_password, password.strip())


def test_email_is_stored_without_surrounding_whitespace(
    api_client,
    db_connection,
    user_data
):
    """
    Verify that the email is stored without leading and trailing
    whitespace.

    The test creates a user through the API with an email surrounded
    by spaces and verifies that the database contains the trimmed email.
    """

    email = user_data["email"]
    user_data["email"] = f"  {email}  "

    response = api_client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 201

    cursor = db_connection.cursor()

    cursor.execute(
        """
        SELECT email
        FROM users
        WHERE email = %s
        """,
        (email,)
    )

    row = cursor.fetchone()

    cursor.close()

    assert row is not None
    assert row[0] == email
