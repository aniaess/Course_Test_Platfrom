import pytest

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
