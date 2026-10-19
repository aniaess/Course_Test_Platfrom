# Course Platform - QA Automation Project

A small course platform created as a practical QA Automation project.

The project combines a simple web application with API, database and automated tests. The main goal is to build a realistic test automation project using Python, Pytest, Playwright, Docker and PostgreSQL.

## Project Architecture

The project consists of three Docker services:

```text
Docker Compose
│
├── db
│   └── PostgreSQL 16
│
├── api
│   └── FastAPI + Uvicorn
│
└── tests
    └── Pytest + Playwright
```

Communication between services:

```text
tests ──────→ api:8000
  │             │
  │             ↓
  └──────────→ db:5432
```

## Technologies

### Application

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- HTML
- CSS
- JavaScript

### Test Automation

- Pytest
- Playwright
- Requests
- Pytest HTML reports

### Infrastructure

- Docker
- Docker Compose
- Git
- GitHub Actions

## Current Features

### Frontend

- Home page
- Registration page
- Login page
- Dashboard page
- Client-side registration validation

### Backend

- FastAPI REST API
- User registration endpoint
- Request validation with Pydantic
- Email validation
- Password length validation
- Duplicate email handling
- Health check endpoint
- Database connectivity endpoint

### Database

PostgreSQL database with a `users` table.

The database is initialized using:

```text
db/init.sql
```

## Automated Tests

The project currently contains tests for:

### API

- Successful user registration
- Invalid email validation
- Password length boundaries
- Duplicate email handling
- API response validation

### Database

- User persistence after registration

### UI

- Successful registration
- Required field validation
- Duplicate email registration

The UI tests use the Page Object Model.

Example structure:

```text
tests/
├── api/
│   ├── client/
│   │   └── api_client.py
│   └── test_users_api.py
│
├── db/
│   └── test_users_db.py
│
└── ui/
    ├── pages/
    │   ├── base_page.py
    │   └── register_page.py
    └── test_register.py
```

## Test Framework

The project contains a small custom test framework with:

- API client abstraction
- Pytest fixtures
- Page Object Model
- Test data generation
- Logging
- Test execution logging
- HTML test reports

The API client provides a common layer for sending HTTP requests:

```python
api_client.post("/users")
api_client.get("/health")
```

The Page Object Model separates UI interaction logic from test scenarios.

## Configuration

The application supports environment-based configuration.

For example, database configuration is read using environment variables:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

The test API URL is also configurable:

```text
BASE_URL
```

Local development values are stored in `.env`.

The `.env` file is excluded from Git using `.gitignore`.

## Running the Project with Docker

Build the Docker images:

```bash
docker compose build
```

Start the services:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

The application API is available at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

Database connectivity check:

```text
http://localhost:8000/db-test
```

## Running Tests

Tests can be executed inside the Docker test container:

```bash
docker compose run --rm tests
```

The test container runs:

- Pytest
- Playwright
- API tests
- Database tests
- UI tests

## Test Reports

Reporting is configured in `pytest.ini`. Every test run produces:

```text
test-results/
├── test-report.html   # pytest-html report
├── junit.xml          # JUnit XML report (with logs of every test)
├── failures.json      # failed tests for AI analysis (created in CI)
└── playwright/        # screenshots and traces of failed UI tests
logs/
└── test.log           # framework logs
```

When the tests run in Docker, `test-results/` and `logs/` are mounted
from the project directory, so the results are available after the
container is removed.

A trace of a failed UI test can be opened with:

```text
playwright show-trace test-results/playwright/<test-name>/trace.zip
```

Both directories are excluded from Git using `.gitignore`.

In GitHub Actions:

- A summary of the results (totals and failed tests) is shown on the workflow run page.
- `scripts/collect_test_failures.py` writes `test-results/failures.json`: for every
  failed test the covered test cases with the expected result (from
  `docs/**/test_cases.md`), the message, traceback, source code of the test,
  its logs and the paths of Playwright screenshots and traces. Long texts are
  shortened and passwords are masked.
- `test-results/` and `logs/` are uploaded as the `test-results` artifact
  (kept for 14 days), also when the tests fail.
- `failures.json` is also uploaded alone as the small `failures` artifact.

## CI/CD

GitHub Actions is configured to run the automated tests.

The intended CI flow is:

```text
GitHub
   ↓
GitHub Actions
   ↓
Docker Compose
   ↓
PostgreSQL
   ↓
FastAPI
   ↓
Pytest + Playwright
```

The workflow is located at:

```text
.github/workflows/tests.yml
```

## Project Goals

The project is being developed incrementally to practice and demonstrate:

- API test automation
- UI test automation
- Database testing
- Page Object Model
- API client design
- Test fixtures
- Logging
- Test reporting
- Docker and Docker Compose
- CI/CD with GitHub Actions
- Environment-based configuration

## Planned Improvements

Future development may include:

- User login and authentication
- User roles (`USER` / `ADMIN`)
- Courses
- Course enrollment
- Authentication testing
- Additional database checks
- Allure reporting
- Expanded GitHub Actions pipeline
- Improved test data management
- More comprehensive API and UI coverage

## AI-Assisted Testing

The project includes a Claude Code subagent for reviewing test quality:

```text
.claude/agents/test-quality-reviewer.md
```

The `test-quality-reviewer` agent reviews API, database and UI tests for:

- Requirements coverage (compared with `docs/requirements/` and `docs/registration/test_cases.md`)
- Assertion quality
- Boundary values
- Test isolation and test data cleanup
- Flakiness risks
- Project conventions (fixtures, Page Object Model, `Messages`, docstrings)

The agent is read-only and never modifies tests or application code. It returns a report with findings grouped by severity, a requirements coverage table and a list of good practices.

### Running the Agent

Start Claude Code in the project directory and check that the agent is available:

```text
/agents
```

Ask Claude Code to use the agent, for example:

```text
Use test-quality-reviewer to review the UI registration tests.

Focus on:
- Playwright assertions and auto-waiting
- Page Object Model usage
- Positive and negative registration scenarios
- Form validation and error messages
- Boundary cases and missing test scenarios
- Test isolation and flakiness

Compare the tests with docs/requirements/registration_requirements.md
and docs/registration/test_cases.md.

Save the report to docs/qa-reports/ui_registration_review.md.

Do not modify any tests or application code.
```

The agent saves the report as a new Markdown file under `docs/qa-reports/`. It does not overwrite existing reports without permission.

Without a specified scope, the agent reviews changed test files. If there are no changes, it reviews the whole `tests/` directory.

## Documentation

- [Registration Requirements](docs/requirements/registration_requirements.md)
- [Registration Test Cases](docs/registration/test_cases.md)
