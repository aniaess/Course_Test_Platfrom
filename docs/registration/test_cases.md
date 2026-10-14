# Registration Test Cases

Test cases for the registration functionality described in
[Registration Requirements](../requirements/registration_requirements.md).

Each test case is mapped to the automated test that covers it.

## 1. UI

| ID | Title | Test data | Expected result | Automated test |
|---|---|---|---|---|
| REG-UI-01 | Successful registration | Valid name, unique email, valid password | Message "Registration successful!" is displayed | `tests/ui/test_register.py::test_user_can_register_successfully` |
| REG-UI-02 | Empty name | name = "" | Message "Name cannot be empty." | `tests/ui/test_register.py::test_user_cannot_register_with_empty_required_field` |
| REG-UI-03 | Empty email | email = "" | Message "Email cannot be empty." | `tests/ui/test_register.py::test_user_cannot_register_with_empty_required_field` |
| REG-UI-04 | Empty password | password = "" | Message "Password cannot be empty." | `tests/ui/test_register.py::test_user_cannot_register_with_empty_required_field` |
| REG-UI-05 | Existing email | Email of an already registered user | Message "User with this email already exists" | `tests/ui/test_register.py::test_user_cannot_register_with_existing_email` |
| REG-UI-06 | Password too short | password = "1234567" (7 characters) | Message "Password must be at least 8 characters long." | `tests/ui/test_register.py::test_user_cannot_register_with_invalid_password_length` |
| REG-UI-07 | Name too short | name = "A" (1 character) | Message "Name is too short." | `tests/ui/test_register.py::test_user_cannot_register_with_invalid_name_length` |
| REG-UI-08 | Server error | Registration request answered with HTTP 500 (mocked) | Message "Something went wrong. Please try again later." | `tests/ui/test_register.py::test_user_sees_error_message_when_server_returns_500` |
| REG-UI-09 | Connection failure | Registration request aborted (mocked) | Message "Cannot connect to the server. Please check your connection." | `tests/ui/test_register.py::test_user_sees_error_message_when_connection_fails` |
| REG-UI-10 | Name too long | name = 101 characters | Message "Name is too long." | `tests/ui/test_register.py::test_user_cannot_register_with_invalid_name_length` |
| REG-UI-11 | Password too long | password = 129 characters | Message "Password must be at most 128 characters long." | `tests/ui/test_register.py::test_user_cannot_register_with_invalid_password_length` |

## 2. API

| ID | Title | Test data | Expected result | Automated test |
|---|---|---|---|---|
| REG-API-01 | Successful registration | Valid name, unique email, valid password | HTTP 201 | `tests/api/test_users_api.py::test_create_user` |
| REG-API-02 | Duplicate email | Email of an already registered user | HTTP 409 | `tests/api/test_users_api.py::test_create_user_with_duplicate_email_returns_409` |
| REG-API-03 | Missing required field | Request without name / email / password | HTTP 422 | `tests/api/test_users_api.py::test_create_user_without_required_field_returns_422` |
| REG-API-04 | Invalid data type | Number instead of a string in a field | HTTP 422 | `tests/api/test_users_api.py::test_create_user_with_invalid_data_type_returns_422` |
| REG-API-05 | Name length boundaries | 1 / 2 / 100 / 101 characters | 422 / 201 / 201 / 422 | `tests/api/test_users_api.py::test_create_user_with_name_length_boundary` |
| REG-API-06 | Invalid email format | "test", "test@", "@test.pl", "test@test", "test.pl", "test@@test.pl" | HTTP 422 | `tests/api/test_users_api.py::test_create_user_with_invalid_email_returns_422` |
| REG-API-07 | Password length boundaries | 7 / 8 / 128 / 129 characters | 422 / 201 / 201 / 422 | `tests/api/test_users_api.py::test_create_user_with_password_length_boundary` |
| REG-API-08 | Response does not expose password | Valid user data | Response contains only id, name, email; no password or Argon2 hash | `tests/api/test_users_api.py::test_create_user_response_does_not_expose_password` |
| REG-API-09 | Blank name | name = "   " / " A " | HTTP 422 | `tests/api/test_users_api.py::test_create_user_with_blank_name_returns_422` |
| REG-API-10 | Name whitespace is trimmed | name = "  Test User  " | HTTP 201, response name is "Test User" | `tests/api/test_users_api.py::test_create_user_trims_name_whitespace` |
| REG-API-11 | Email whitespace is trimmed | email surrounded by spaces | HTTP 201, response email has no surrounding spaces | `tests/api/test_users_api.py::test_create_user_trims_email_whitespace` |
| REG-API-12 | Existing email with surrounding spaces | Email of an already registered user surrounded by spaces | HTTP 409 | `tests/api/test_users_api.py::test_create_user_with_existing_email_surrounded_by_whitespace_returns_409` |

## 3. Database

| ID | Title | Test data | Expected result | Automated test |
|---|---|---|---|---|
| REG-DB-01 | User is persisted | User created through the API | Row with matching name and email exists in `users` | `tests/db/test_users_db.py::test_created_user_is_persisted_in_database` |
| REG-DB-02 | Email is unique | Insert of a duplicate email | Database rejects the insert | `tests/db/test_users_db.py::test_user_email_must_be_unique` |
| REG-DB-03 | Required fields are NOT NULL | NULL in name / email / password | Database rejects the insert | `tests/db/test_users_db.py::test_user_required_fields_cannot_be_null` |
| REG-DB-04 | Table structure | - | `users` table has the expected columns | `tests/db/test_users_db.py::test_users_table_has_expected_columns` |
| REG-DB-05 | Password not stored in plaintext | User created through the API | Stored value differs from the password | `tests/db/test_users_db.py::test_password_is_not_stored_in_plaintext` |
| REG-DB-06 | Password stored as Argon2id hash | User created through the API | Stored value starts with `$argon2id$` and has at most 255 characters | `tests/db/test_users_db.py::test_password_is_stored_as_argon2id_hash` |
| REG-DB-07 | Unique salt per password | Two users with the same password | Stored values are different | `tests/db/test_users_db.py::test_same_password_produces_different_stored_values` |
| REG-DB-08 | Name stored trimmed | name = "  Test User  " | Stored name is "Test User" | `tests/db/test_users_db.py::test_name_is_stored_without_surrounding_whitespace` |
| REG-DB-09 | Password whitespace preserved | password = "  secret123  " | Hash matches the password with spaces, not the trimmed one | `tests/db/test_users_db.py::test_password_whitespace_is_preserved` |
| REG-DB-10 | Email stored trimmed | email surrounded by spaces | Stored email has no surrounding spaces | `tests/db/test_users_db.py::test_email_is_stored_without_surrounding_whitespace` |

## 4. Not Yet Covered

These cases depend on the open questions in the requirements:

- Invalid email format in the UI.
- Case-insensitive email uniqueness.
- Password complexity rules.
- Rate limiting of registration requests.
