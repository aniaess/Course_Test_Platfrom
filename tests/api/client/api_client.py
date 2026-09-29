import requests

from utils.logger import get_logger


class ApiClient:
    """Client used to communicate with the Course Platform API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = get_logger(__name__)

    def post(self, endpoint: str, **kwargs):
        self.logger.info(f"POST {endpoint}")

        response = requests.post(
            f"{self.base_url}{endpoint}",
            **kwargs
        )

        self.logger.info(
            f"Response status: {response.status_code}"
        )

        return response

    def get(self, endpoint: str, **kwargs):
        self.logger.info(f"GET {endpoint}")

        response = requests.get(
            f"{self.base_url}{endpoint}",
            **kwargs
        )

        self.logger.info(
            f"Response status: {response.status_code}"
        )

        return response