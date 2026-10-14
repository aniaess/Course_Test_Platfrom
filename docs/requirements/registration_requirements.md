# Registration Requirements

## 1. Purpose

The registration functionality allows a new user
to create an account on the Course Platform.

## 2. Registration Fields

The registration form contains three required fields:

- name
- email
- password

## 3. Name Requirements

- The name is required.
- Leading and trailing whitespace is removed before validation
  and storage.
- A name made only of whitespace is rejected.
- The minimum length is 2 characters.
- The maximum length is 100 characters.
- Names shorter than 2 characters must be rejected.
- Names longer than 100 characters must be rejected.

## 4. Email Requirements

- The email is required.
- Leading and trailing whitespace is removed before validation
  and storage.
- The email must have a valid format.
- The email must be unique.
- Registering an existing email returns HTTP 409.
- Invalid email formats submitted to the API
  return HTTP 422.

## 5. Password Requirements

- The password is required.
- Whitespace in the password is preserved, including leading
  and trailing spaces.
- The minimum length is 8 characters.
- Passwords shorter than 8 characters are rejected.
- The maximum length is 128 characters.
- Passwords longer than 128 characters are rejected.
- Additional password complexity requirements
  have not yet been defined.

## 6. API Requirements

| Operation | Expected HTTP status |
|---|---|
| Successful registration | 201 |
| Registration with an existing email | 409 |
| Missing required field | 422 |
| Invalid data type | 422 |
| Invalid email format | 422 |
| Value outside defined length limits | 422 |

- A successful registration returns only the public user
  fields: `id`, `name` and `email`.
- A 422 response identifies the invalid field
  in `detail[].loc`.

## 7. UI Requirements

The registration form validates the input before sending
the request and displays one of the following messages:

| Situation | Message |
|---|---|
| Successful registration | Registration successful! |
| Empty name | Name cannot be empty. |
| Name shorter than 2 characters | Name is too short. |
| Name longer than 100 characters | Name is too long. |
| Empty email | Email cannot be empty. |
| Empty password | Password cannot be empty. |
| Password shorter than 8 characters | Password must be at least 8 characters long. |
| Password longer than 128 characters | Password must be at most 128 characters long. |
| Existing email (HTTP 409) | User with this email already exists |
| Server error or any other unexpected status | Something went wrong. Please try again later. |
| Server cannot be reached | Cannot connect to the server. Please check your connection. |

- The success message uses the `success-message` style;
  all other messages use the `error-message` style.

## 8. Data Integrity and Security

- User data must be persisted in PostgreSQL.
- The `users` table contains the columns `id` (integer),
  `name` (VARCHAR(100)), `email` (VARCHAR(255))
  and `password` (VARCHAR(255)).
- Email addresses must be unique.
- Required database fields must not be NULL.
- Passwords must not be stored in plaintext.
- Passwords are hashed with Argon2id and stored as a PHC string
  (prefix `$argon2id$`) of at most 255 characters.
- Each password hash uses its own random salt, so the same password
  produces a different stored value for each user.
- API responses must never contain the password
  or its hash.

## 9. Open Questions

The following rules require clarification:

- Is email comparison case-sensitive?
- Are additional password complexity rules required?
- Is rate limiting required?