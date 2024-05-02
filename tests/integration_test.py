import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app, load_data, TestConfig, save_data  # noqa
from flask import Response  # noqa


class TestIntegrationServerApp:
    def setup_method(self):
        app.config.from_object(TestConfig)
        self.known_email = "lifters@test.com"
        self.unkonwn_email = "admin@unknown.fr"
        self.competitions, self.clubs = load_data()

    def test_user_journey(self):
        # test that the user can login, view the board, book a place and logout
        with app.test_client() as client:
            # User can access the home page
            response: Response = client.get("/")
            assert response.status_code == 200
            assert b"Please enter your secretary email to continue" in response.data
            response: Response = client.post(
                "/showSummary", data={"email": self.known_email}
            )
            assert response.status_code == 200
            assert f"Welcome, {self.known_email}".encode() in response.data
            # User can view the Points Board and can book a place
            assert b"See Club Points Board" in response.data
            assert b"Book Places" in response.data
            # User can view the Points Board, then purchase a competition place
            response: Response = client.get("/points")
            assert response.status_code == 200
            competition = self.competitions[0]
            club = self.clubs[0]
            PLACES_PURCHASED = 2
            original_points = int(club["points"])
            original_number_of_places = int(competition["numberOfPlaces"])
            response: Response = client.post(
                "/purchasePlaces",
                data={
                    "competition": competition["name"],
                    "club": club["name"],
                    "places": PLACES_PURCHASED,
                },
            )
            assert response.status_code == 200
            assert b"Great-booking complete!" in response.data

            updated_competitions, updated_clubs = load_data()
            # Check that the club's points were deducted correctly
            updated_competitions, updated_clubs = load_data()
            if updated_clubs[0]["name"] == club["name"]:
                assert (
                    int(updated_clubs[0]["points"])
                    == original_points - PLACES_PURCHASED
                )
            assert (
                f"Points available: {original_points - PLACES_PURCHASED}".encode()
                in response.data
            )
            # Check that the competition's number of places was updated correctly
            if updated_competitions[0]["name"] == competition["name"]:
                assert (
                    int(updated_competitions[0]["numberOfPlaces"])
                    == original_number_of_places - PLACES_PURCHASED
                )
            assert (
                "Number of Places:"
                f"{original_number_of_places - PLACES_PURCHASED}".encode()
                in response.data
            )

            # Set the club's points and competitions number of places
            # back to the original points
            club["points"] = str(original_points)
            competition["numberOfPlaces"] = str(original_number_of_places)
            save_data(self.competitions, self.clubs)

            # User can logout
            response: Response = client.get("/logout", follow_redirects=True)
            assert response.status_code == 200
            assert b"Please enter your secretary email to continue" in response.data
