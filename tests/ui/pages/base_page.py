from playwright.sync_api import Page

from utils.logger import get_logger


class BasePage:
    """Base class for all page objects."""

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(__name__)

    def open(self, url: str):
        """Open the specified page URL."""

        self.logger.info(f"Opening page: {url}")

        self.page.goto(url)