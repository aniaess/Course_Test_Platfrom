import uuid

from pathlib import Path

import pytest
from _pytest.reports import TestReport

from app.database import get_connection
from tests.api.client.api_client import ApiClient
from tests.config import BASE_URL
from utils.logger import get_logger, log_separator
from tests.ui.pages.register_page import RegisterPage


logger = get_logger(__name__)
REPORT_KEY = pytest.StashKey[TestReport]()


@pytest.fixture
def db_connection():
    """Provide a database connection for a test."""

    logger.info("Connecting to database")

    connection = get_connection()

    logger.info("Database connection established")

    yield connection

    logger.info("Closing database connection")

    connection.close()

    logger.info("Database connection closed")


@pytest.fixture
def api_client():
    """Provide an API client for a test."""

    logger.info(f"Creating API client with base URL: {BASE_URL}")

    return ApiClient(BASE_URL)


@pytest.fixture
def clean_database(db_connection):
    """Clean test data before and after each test."""

    logger.info("Cleaning database before test")

    cursor = db_connection.cursor()

    cursor.execute("DELETE FROM users")

    db_connection.commit()

    logger.info("Database cleaned before test")

    yield

    logger.info("Cleaning database after test")

    cursor.execute("DELETE FROM users")

    db_connection.commit()

    cursor.close()

    logger.info("Database cleaned after test")


@pytest.fixture
def register_page(page):
    """Provide a RegisterPage object for a UI test."""

    logger.info("Creating RegisterPage")

    return RegisterPage(page)


@pytest.fixture
def user_data():
    """Provide unique test data for user registration."""

    user_data = {
        "name": "Playwright User",
        "email": f"playwright-{uuid.uuid4()}@test.pl",
        "password": "secret123"
    }

    logger.info(
        f"Generated test user data for email: {user_data['email']}"
    )

    return user_data


def pytest_runtest_makereport(item, call):
    """
    Store the test report for later use by fixtures.
    """

    if call.when == "call":
        report = TestReport.from_item_and_call(item, call)
        item.stash[REPORT_KEY] = report


@pytest.fixture(autouse=True)
def log_test_execution(request):
    """Log the start, result and end of every test."""

    log_separator()

    logger.info(
        f"START TEST: {request.node.nodeid}"
    )

    yield

    report = request.node.stash.get(REPORT_KEY, None)

    if report is not None:
        if report.passed:
            logger.info(
                f"TEST PASSED: {request.node.nodeid}"
            )

        elif report.failed:
            logger.error(
                f"TEST FAILED: {request.node.nodeid}"
            )

            logger.error(
                f"TRACEBACK:\n{report.longrepr}"
            )

        elif report.skipped:
            logger.warning(
                f"TEST SKIPPED: {request.node.nodeid}"
            )

    logger.info(
        f"END TEST: {request.node.nodeid}"
    )

    log_separator()