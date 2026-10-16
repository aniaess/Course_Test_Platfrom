from playwright.sync_api import Page

from tests.config import BASE_URL
from tests.ui.pages.base_page import BasePage


class RegisterPage(BasePage):
    """Page object for the registration page."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.name_input = page.locator("#name")
        self.email_input = page.locator("#email")
        self.password_input = page.locator("#password")
        self.register_button = page.locator('#register-form button[type="submit"]')
        self.register_message = page.locator("#register-message")
        self.login_button = page.locator("#login-button")

    def open(self):
        """Open the registration page."""

        super().open(f"{BASE_URL}/register")

    def register_user(
        self,
        name: str,
        email: str,
        password: str
    ):
        """Fill in the registration form and submit it."""

        self.logger.info(
            f"Registering user with email: {email}"
        )

        self.name_input.fill(name)
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.register_button.click()

        self.logger.info("Registration form submitted")

    def get_message(self):
        """Return the registration message locator."""

        self.logger.info("Getting registration message")

        return self.register_message