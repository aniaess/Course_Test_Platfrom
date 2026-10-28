## 🤖 AI analysis of test failures

Failed: 4, errors: 0, total: 7. Model: `claude-opus-5-5`.

4 of 7 tests failed, each for a different reason; there is no shared root cause and no sign of environment problems, since every API call reached the service and returned a response. Two failures are application bugs: the password is hashed with Argon2i instead of Argon2id, and a duplicate email returns HTTP 400 instead of 409. Two are test bugs: the UI test asserts a page title the application does not use, and the boundary test expects 422 for a 2-character name that the test case says must be accepted.

| Test | Category | Confidence |
| --- | --- | --- |
| `tests/db/test_users_db.py::test_password_is_stored_as_argon2id_hash` | 🐞 Application bug | high |
| `tests/api/test_users_api.py::test_create_user_with_duplicate_email_returns_409` | 🐞 Application bug | high |
| `tests/ui/test_register.py::test_user_can_go_to_login_page_after_registration[chromium]` | 🧪 Test bug | high |
| `tests/api/test_users_api.py::test_create_user_with_name_length_boundary[AB-422]` | 🧪 Test bug | high |

### `tests/db/test_users_db.py::test_password_is_stored_as_argon2id_hash`

**Test cases:** REG-DB-06

**Category:** 🐞 Application bug (high)

**Observed behavior:** The user was created (HTTP 201), but the stored password value starts with '$argon2i$' (Argon2i variant), not '$argon2id$'.

**Expected behavior:** REG-DB-06: the stored value starts with `$argon2id$` and has at most 255 characters.

**Evidence:**

```text
'$argon2i$v=19$m=65536,t=3,p=4$dYhRmnMl8YctjNcuDGZcNg$7VLdbVwZPSCRRcwnB7WWBHjBN0hI8u/4rpVgXBfRPKc'.startswith
AssertionError: assert False
tests.api.client.api_client | Response status: 201
tests/db/test_users_db.py:258: AssertionError
```

**Possible root cause (hypothesis):** The password hasher in the application is configured with the Argon2i variant instead of Argon2id. For example, argon2-cffi is used with Type.I, or passlib is set to argon2 type 'i'.

**Recommended next steps:**

- Inspect the password hashing configuration in the application (hasher type/variant parameter) and switch it to Argon2id.
- Confirm password verification still works for existing Argon2i hashes, or plan a rehash on login.
- Re-run REG-DB-06; the length check (<= 255) was not reached and should be verified after the fix.

### `tests/api/test_users_api.py::test_create_user_with_duplicate_email_returns_409`

**Test cases:** REG-API-02

**Category:** 🐞 Application bug (high)

**Observed behavior:** The first POST /users with a unique email returned 201. The second POST with the same data returned 400 instead of 409.

**Expected behavior:** REG-API-02: registering an already registered email returns HTTP 409.

**Evidence:**

```text
assert 400 == 409
+  where 400 = <Response [400]>.status_code
tests.api.client.api_client | Response status: 201
tests.api.client.api_client | Response status: 400
```

**Possible root cause (hypothesis):** The duplicate-email check in the user creation endpoint likely raises HTTPException with status 400 instead of 409 Conflict. Another possibility is that a database IntegrityError is mapped to 400. The response body was not captured, so the exact error message is not confirmed.

**Recommended next steps:**

- Log or inspect the response body of the second request to confirm the duplicate-email detail message.
- Change the duplicate-email handling in the /users endpoint to return 409 Conflict.
- Re-run the test so the Messages.EMAIL_ALREADY_EXISTS detail assertion is also checked.

### `tests/ui/test_register.py::test_user_can_go_to_login_page_after_registration[chromium]`

**Test cases:** REG-UI-12

**Category:** 🧪 Test bug (high)

**Observed behavior:** After registration and a click on the login button, the login page was displayed: heading 'Login', the text 'Sign in to your account.', Email and Password textboxes and a Login button. Its title was 'Login - AI Academy'. The test expected the title 'Login - Course Platform'.

**Expected behavior:** REG-UI-12: the login page is opened. The test case does not specify a page title.

**Evidence:**

```text
AssertionError: Page title expected to be 'Login - Course Platform'
Actual value: Login - AI Academy
14 × locator resolved to <html lang="en">…</html>
- unexpected value "Login - AI Academy"
- heading "Login" [level=1]
- paragraph: Sign in to your account.
- text: AI Academy
tests/ui/test_register.py:63: AssertionError
```

**Possible root cause (hypothesis):** The test hardcodes an outdated or incorrect product name in the expected title. The application consistently brands itself 'AI Academy' (banner text and title), and the login page did open as the test case expects.

**Recommended next steps:**

- Update the expected title to 'Login - AI Academy', or better, assert on the URL or the 'Login' heading.
- Move the expected page title or brand name into a shared constant (e.g. Messages/config) so it is not duplicated across tests.
- Check with the product owner that 'AI Academy' is the intended brand name.

### `tests/api/test_users_api.py::test_create_user_with_name_length_boundary[AB-422]`

**Test cases:** REG-API-05

**Category:** 🧪 Test bug (high)

**Observed behavior:** A POST /users request with the 2-character name 'AB' returned 201. The test parametrization expects 422 for this case.

**Expected behavior:** REG-API-05: name lengths 1 / 2 / 100 / 101 characters give 422 / 201 / 201 / 422, so a 2-character name should return 201.

**Evidence:**

```text
assert 201 == 422
("AB", 422),       # 2 characters - minimum
The minimum allowed length is 2 characters and the maximum\n    allowed length is 100 characters.
expected_result": "422 / 201 / 201 / 422"
tests.api.client.api_client | Response status: 201
```

**Possible root cause (hypothesis):** The parametrize entry for 'AB' has the wrong expected status (422 instead of 201). This contradicts the test case, the inline comment and the docstring. The application behaves correctly, and the other three boundary cases passed.

**Recommended next steps:**

- Change the parametrize entry to ("AB", 201).
- Review the other parametrized boundary data against the REG-API-05 test case table.

_The analysis was generated by AI and can be wrong. Check it before you act on it._
