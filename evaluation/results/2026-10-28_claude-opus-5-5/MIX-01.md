## 🤖 AI analysis of test failures

Failed: 4, errors: 0, total: 7. Model: `claude-opus-5-5`.

Of 7 tests, 4 failed, each for a different reason; no two failures share a root cause. Two are application bugs: passwords are hashed with Argon2i instead of Argon2id, and a duplicate email returns HTTP 400 instead of 409. The other two are test bugs: the UI test asserts a page title that does not match the application's 'AI Academy' branding, and the name-boundary test expects 422 for a valid 2-character name. The API and database were reachable throughout, so there are no signs of an environment problem.

| Test | Category | Confidence |
| --- | --- | --- |
| `tests/db/test_users_db.py::test_password_is_stored_as_argon2id_hash` | 🐞 Application bug | high |
| `tests/api/test_users_api.py::test_create_user_with_duplicate_email_returns_409` | 🐞 Application bug | high |
| `tests/ui/test_register.py::test_user_can_go_to_login_page_after_registration[chromium]` | 🧪 Test bug | high |
| `tests/api/test_users_api.py::test_create_user_with_name_length_boundary[AB-422]` | 🧪 Test bug | high |

### `tests/db/test_users_db.py::test_password_is_stored_as_argon2id_hash`

**Test cases:** REG-DB-06

**Category:** 🐞 Application bug (high)

**Observed behavior:** The user was created successfully (HTTP 201). The stored password value starts with '$argon2i$' rather than '$argon2id$', so the startswith assertion failed.

**Expected behavior:** REG-DB-06: the stored value starts with `$argon2id$` and has at most 255 characters.

**Evidence:**

```text
'$argon2i$v=19$m=65536,t=3,p=4$dYhRmnMl8YctjNcuDGZcNg$7VLdbVwZPSCRRcwnB7WWBHjBN0hI8u/4rpVgXBfRPKc'.startswith
assert stored_password.startswith("$argon2id$")
2026-10-26 12:57:06,112 | INFO | tests.api.client.api_client | Response status: 201
```

**Possible root cause (hypothesis):** The application's password hasher is set to the Argon2i variant (for example, argon2 Type.I or a passlib scheme other than argon2id) instead of Argon2id.

**Recommended next steps:**

- Check the password hashing configuration in the application and switch it to Argon2id (type=ID).
- Decide how to handle existing Argon2i hashes, for example rehashing them on the user's next login.
- Re-run REG-DB-06 after the fix.

### `tests/api/test_users_api.py::test_create_user_with_duplicate_email_returns_409`

**Test cases:** REG-API-02

**Category:** 🐞 Application bug (high)

**Observed behavior:** The first POST /users returned 201. The second POST with the same email returned 400 instead of 409.

**Expected behavior:** REG-API-02: registering an email that is already in use returns HTTP 409.

**Evidence:**

```text
assert 400 == 409
2026-10-26 12:57:06,370 | INFO | tests.api.client.api_client | Response status: 201
2026-10-26 12:57:06,535 | INFO | tests.api.client.api_client | Response status: 400
```

**Possible root cause (hypothesis):** The duplicate-email check in the application raises HTTPException with status 400 instead of 409 Conflict. The response body was not captured, so the error message cannot be checked.

**Recommended next steps:**

- Find the duplicate-email handling in the users endpoint/service and change the status code to 409.
- Log or capture the body of the 400 response to confirm that it is the duplicate-email error.
- Re-run REG-API-02.

### `tests/ui/test_register.py::test_user_can_go_to_login_page_after_registration[chromium]`

**Test cases:** REG-UI-12

**Category:** 🧪 Test bug (high)

**Observed behavior:** After registering and clicking 'Log in', the browser showed a page titled 'Login - AI Academy', with a 'Login' heading, Email and Password textboxes and a Login button. The test expected the title 'Login - Course Platform'. Playwright resolved the element 14 times over the 5 s timeout and saw the same title every time.

**Expected behavior:** REG-UI-12: the login page is opened.

**Evidence:**

```text
Page title expected to be 'Login - Course Platform'
Actual value: Login - AI Academy
14 × locator resolved to <html lang="en">…</html>
- unexpected value "Login - AI Academy"
- heading "Login" [level=1]
- banner:
  - text: AI Academy
expect(register_page.page).to_have_title("Login - Course Platform")
```

**Possible root cause (hypothesis):** The test hardcodes a title using the brand name 'Course Platform', but the application is branded 'AI Academy' (both the banner and the title). The login page did open, so the application met the test case's expected result. The title stayed the same through all retries, so this was not a timing issue.

**Recommended next steps:**

- Change the assertion to 'Login - AI Academy', or read the expected title from a shared constant or page object.
- Optionally assert on the login page URL or the 'Login' heading instead of the brand-dependent title.
- Confirm with product which brand name is the intended one.

### `tests/api/test_users_api.py::test_create_user_with_name_length_boundary[AB-422]`

**Test cases:** REG-API-05

**Category:** 🧪 Test bug (high)

**Observed behavior:** POST /users with the 2-character name 'AB' returned 201, but the parametrized test expected 422.

**Expected behavior:** REG-API-05: names of 1 / 2 / 100 / 101 characters should give 422 / 201 / 201 / 422, so a 2-character name should return 201.

**Evidence:**

```text
assert 201 == 422
("AB", 422),       # 2 characters - minimum
The minimum allowed length is 2 characters and the maximum
    allowed length is 100 characters.
2026-10-26 12:57:14,440 | INFO | tests.api.client.api_client | Response status: 201
```

**Possible root cause (hypothesis):** The parametrize data has the wrong expected status for 'AB'. Its own comment and docstring say 2 characters is the allowed minimum, which should give 201. The application behaves as the test case specifies.

**Recommended next steps:**

- Change the parametrize entry to ("AB", 201).
- Review the remaining boundary data against REG-API-05. The other three cases passed and match the specification.

_The analysis was generated by AI and can be wrong. Check it before you act on it._
