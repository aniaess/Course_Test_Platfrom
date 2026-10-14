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
- A maximum password length has not yet been defined.
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

## 7. Data Integrity and Security

- User data must be persisted in PostgreSQL.
- Email addresses must be unique.
- Required database fields must not be NULL.
- Passwords must not be stored in plaintext.
- API responses must not unnecessarily expose
  sensitive information.

## 8. Open Questions

The following rules require clarification:

- Is email comparison case-sensitive?
- Is there a maximum password length?
- Are additional password complexity rules required?
- Is rate limiting required?