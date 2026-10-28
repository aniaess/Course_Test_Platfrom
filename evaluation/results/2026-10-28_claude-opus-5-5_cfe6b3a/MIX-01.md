## 🤖 AI analysis of test failures

Failed: 4, errors: 0, total: 7. Model: `claude-opus-5-5`.

Of 7 tests, 4 failed for four unrelated reasons, with no shared root cause and no sign of environment problems. Two are application bugs: passwords are hashed with Argon2i instead of Argon2id, and a duplicate email returns 400 instead of 409. The other two are test bugs: a wrong expected page title in the UI test, and wrong expected data (422 instead of 201) for the 2-character name boundary.

| Test | Category | Confidence |
| --- | --- | --- |
| `tests/db/test_users_db.py::test_password_is_stored_as_argon2id_hash` | 🐞 Application bug | high |
| `tests/api/test_users_api.py::test_create_user_with_duplicate_email_returns_409` | 🐞 Application bug | high |
| `tests/ui/test_register.py::test_user_can_go_to_login_page_after_registration[chromium]` | 🧪 Test bug | high |
| `tests/api/test_users_api.py::test_create_user_with_name_length_boundary[AB-422]` | 🧪 Test bug | high |

### `tests/db/test_users_db.py::test_password_is_stored_as_argon2id_hash`

**Test cases:** REG-DB-06

**Category:** 🐞 Application bug (high)

**Observed behavior:** The user was created successfully (HTTP 201). The password stored in the database starts with the prefix '$argon2i$' (Argon2i variant) instead of '$argon2id$'.

**Expected behavior:** Per REG-DB-06, the stored value starts with `$argon2id$` and has at most 255 characters.

**Evidence:**

```text
2026-10-26 12:57:06,112 | INFO | tests.api.client.api_client | Response status: 201
AssertionError: assert False
'$argon2i$v=19$m=65536,t=3,p=4$dYhRmnMl8YctjNcuDGZcNg$7VLdbVwZPSCRRcwnB7WWBHjBN0hI8u/4rpVgXBfRPKc'.startswith
tests/db/test_users_db.py:258: AssertionError
```

**Possible root cause (hypothesis):** The password hasher is configured with the Argon2i variant instead of Argon2id. Examples: argon2-cffi used with type=Type.I, or a passlib/hash configuration selecting 'i' rather than 'id'.

**Recommended next steps:**

- Inspect the password hashing configuration in the application (hasher type/variant parameter) and switch it to Argon2id.
- Check whether existing users have Argon2i hashes and plan rehash-on-login if needed.
- Re-run REG-DB-06 after the fix.

### `tests/api/test_users_api.py::test_create_user_with_duplicate_email_returns_409`

**Test cases:** REG-API-02

**Category:** 🐞 Application bug (high)

**Observed behavior:** The first POST /users with a freshly generated unique email returned 201. The second POST with the same data returned HTTP 400.

**Expected behavior:** Per REG-API-02, registering with the email of an already registered user returns HTTP 409.

**Evidence:**

```text
2026-10-26 12:57:06,370 | INFO | tests.api.client.api_client | Response status: 201
2026-10-26 12:57:06,535 | INFO | tests.api.client.api_client | Response status: 400
assert 400 == 409
tests/api/test_users_api.py:58: AssertionError
```

**Possible root cause (hypothesis):** The duplicate-email check in the user creation endpoint raises HTTPException with status 400 instead of 409 Conflict. The response body was not captured, so the exact error message is unknown.

**Recommended next steps:**

- Change the duplicate-email handling in the POST /users endpoint to return 409 Conflict.
- Log or inspect the 400 response body to confirm it is the duplicate-email error.
- Re-run REG-API-02, which also verifies the detail message.

### `tests/ui/test_register.py::test_user_can_go_to_login_page_after_registration[chromium]`

**Test cases:** REG-UI-12

**Category:** 🧪 Test bug (high)

**Observed behavior:** After registration, the 'Log in' button was clicked and the login page was opened. It shows the heading 'Login', Email and Password textboxes and a 'Login' button. The page title is 'Login - AI Academy', and the banner also shows 'AI Academy'.

**Expected behavior:** Per REG-UI-12, the login page is opened. The test additionally asserts the title 'Login - Course Platform'.

**Evidence:**

```text
AssertionError: Page title expected to be 'Login - Course Platform'
Actual value: Login - AI Academy
- heading "Login" [level=1]
- textbox "Email"
- textbox "Password"
- button "Login"
expect(register_page.page).to_have_title("Login - Course Platform")
```

**Possible root cause (hypothesis):** The application did what the test case requires and opened the login page. The test asserts an outdated or wrong page title: the app's branding is 'AI Academy' (visible in both title and banner), not 'Course Platform'.

**Recommended next steps:**

- Update the expected title to 'Login - AI Academy'. Alternatively, assert on the URL or the 'Login' heading, which is more robust than branding text.
- Check other UI tests for the same hard-coded 'Course Platform' title.
- Confirm with the product owner that 'AI Academy' is the intended branding.

### `tests/api/test_users_api.py::test_create_user_with_name_length_boundary[AB-422]`

**Test cases:** REG-API-05

**Category:** 🧪 Test bug (high)

**Observed behavior:** POST /users with a 2-character name 'AB' returned HTTP 201. The test parametrization expects 422 for this value.

**Expected behavior:** Per REG-API-05 (1/2/100/101 characters -> 422/201/201/422), a 2-character name should be accepted with HTTP 201.

**Evidence:**

```text
("AB", 422),       # 2 characters - minimum
The minimum allowed length is 2 characters and the maximum allowed length is 100 characters.
2026-10-26 12:57:14,440 | INFO | tests.api.client.api_client | Response status: 201
assert 201 == 422
```

**Possible root cause (hypothesis):** The parametrize entry for 'AB' has the wrong expected status code. The test case, the inline comment ('minimum') and the docstring all say 2 characters is the allowed minimum, so the expected status should be 201. The application behaves correctly.

**Recommended next steps:**

- Change the parametrize entry to ("AB", 201).
- Re-run the boundary test; the other three parameters already pass consistently with REG-API-05.

_The analysis was generated by AI and can be wrong. Check it before you act on it._
