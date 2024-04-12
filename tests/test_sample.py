import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app
import html
from flask import Response


class TestServerApp:
    def setup_method(self):
        self.known_email = "admin@irontemple.com"
        self.unkonwn_email = "admin@irontemple.fr"

    def test_showSummary_known_email(self):
        with app.test_client() as client:
            response: Response = client.post(
                "/showSummary", data={"email": self.known_email}
            )
            assert response.status_code == 200
            assert f"Welcome, {self.known_email}".encode() in response.data

    def test_showSummary_unknown_email(self):
        with app.test_client() as client:
            response: Response = client.post(
                "/showSummary", data={"email": self.unkonwn_email}
            )
            assert response.status_code == 404
            # Handle the escaped HTML (' -> &#39;)
            response_data: str = html.unescape(response.data.decode())
            assert (
                "Sorry, we don't have your email address in our records. Please try again or contact the club."
                in response_data
            )
            assert f"Welcome, {self.unkonwn_email}".encode() not in response.data
