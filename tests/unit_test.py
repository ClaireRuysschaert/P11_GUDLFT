import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app, load_data, TestConfig, save_data  # noqa
import html  # noqa
from flask import Response  # noqa


class TestUnitServerApp:
    def setup_method(self):
        app.config.from_object(TestConfig)
        self.known_email = "lifters@test.com"
        self.unkonwn_email = "admin@unknown.fr"
        self.competitions, self.clubs = load_data()

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
                "Sorry, we don't have your email address in our records."
                "Please try again or contact the club."
                in response_data
            )
            assert f"Welcome, {self.unkonwn_email}".encode() not in response.data

    def test_showSummary_no_email(self):
        with app.test_client() as client:
            response: Response = client.post("/showSummary", data={"email": ""})
            assert response.status_code == 404
            assert b"Please enter your email address" in response.data
            assert f"Welcome, {self.unkonwn_email}".encode() not in response.data

    def test_purchasePlaces_all_clubs(self):
        """Test that all clubs can purchase places in the competition
        and that the points are deducted correctly. If the club doesn't
        have enough points, the purchase should fail.
        """
        with app.test_client() as client:
            competition = self.competitions[0]
            PLACES_PURCHASED = 2

            for club in self.clubs:
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

                if original_points >= PLACES_PURCHASED:
                    assert response.status_code == 200
                    assert b"Great-booking complete!" in response.data

                    # Check that the club's points were deducted correctly
                    updated_competitions, updated_clubs = load_data()
                    for updated_club in updated_clubs:
                        if updated_club["name"] == club["name"]:
                            assert (
                                int(updated_club["points"])
                                == original_points - PLACES_PURCHASED
                            )

                    # Check that the competition's number of places was updated
                    # correctly
                    for updated_competition in updated_competitions:
                        if updated_competition["name"] == competition["name"]:
                            assert (
                                int(updated_competition["numberOfPlaces"])
                                == original_number_of_places - PLACES_PURCHASED
                            )
                else:
                    assert response.status_code == 400
                    # Handle the escaped HTML (' -> &#39;)
                    response_data: str = html.unescape(response.data.decode())
                    assert (
                        "Sorry, you don't have enough points to purchase"
                        f"{PLACES_PURCHASED} places."
                        in response_data
                    )

                # Set the club's points and competitions number of places
                # back to the original points
                club["points"] = str(original_points)
                competition["numberOfPlaces"] = str(original_number_of_places)
                save_data(self.competitions, self.clubs)

    def test_purchasePlaces_not_enough_places_in_competition(self):
        """Test that a club cannot purchase more places than the competition
        has available."""
        with app.test_client() as client:
            # 1 place left in the competition
            competition = self.competitions[1]
            club = self.clubs[0]
            original_points = int(club["points"])
            original_number_of_places = int(competition["numberOfPlaces"])

            response: Response = client.post(
                "/purchasePlaces",
                data={
                    "competition": competition["name"],
                    "club": club["name"],
                    "places": original_number_of_places + 1,
                },
            )

            assert response.status_code == 400
            # Handle the escaped HTML (' -> &#39;)
            response_data: str = html.unescape(response.data.decode())
            assert (
                "Sorry, there are not enough places left in this competition"
                f"to purchase {original_number_of_places + 1} places."
                in response_data
            )

            # Set the club's points and competitions number of places
            # back to the original points
            club["points"] = str(original_points)
            competition["numberOfPlaces"] = str(original_number_of_places)
            save_data(self.competitions, self.clubs)

    def test_purchasePlaces_more_than_12_places_in_competition(self):
        """Test that a club cannot purchase more than 12 places at a time
        even if it has enough points."""
        with app.test_client() as client:
            # There is 23 places left to purchase in this competition
            competition = self.competitions[1]
            # Club with 20 points
            club = self.clubs[2]
            original_points = int(club["points"])
            original_number_of_places = int(competition["numberOfPlaces"])

            response: Response = client.post(
                "/purchasePlaces",
                data={
                    "competition": competition["name"],
                    "club": club["name"],
                    "places": 13,
                },
            )

            assert response.status_code == 400
            # Handle the escaped HTML (' -> &#39;)
            response_data: str = html.unescape(response.data.decode())
            assert (
                "Sorry, you can't purchase more than 12 places at a time."
                in response_data
            )

            # Set the club's points and competitions number of places back
            # to the original points
            club["points"] = str(original_points)
            competition["numberOfPlaces"] = str(original_number_of_places)
            save_data(self.competitions, self.clubs)

    def test_purchasePlaces_not_past_competition(self):
        """Test that a club cannot purchase places in a competition
        that has already passed."""
        with app.test_client() as client:
            # Competition that has already passed
            competition = self.competitions[4]
            club = self.clubs[0]
            original_points = int(club["points"])
            original_number_of_places = int(competition["numberOfPlaces"])

            response: Response = client.post(
                "/purchasePlaces",
                data={
                    "competition": competition["name"],
                    "club": club["name"],
                    "places": 1,
                },
            )

            assert response.status_code == 400
            # Handle the escaped HTML (' -> &#39;)
            response_data: str = html.unescape(response.data.decode())
            assert "Sorry, this competition has already taken place." in response_data

            # Set the club's points and competitions number of places
            # back to the original points
            club["points"] = str(original_points)
            competition["numberOfPlaces"] = str(original_number_of_places)
            save_data(self.competitions, self.clubs)

    def test_purchasePlaces_invalid_club_or_competition(self):
        with app.test_client() as client:
            response: Response = client.post(
                "/purchasePlaces",
                data={
                    "competition": self.competitions[0]["name"],
                    "club": "Invalid Club",
                    "places": 1,
                },
            )
            assert response.status_code == 400
            assert b"Sorry, something went wrong. Please try again." in response.data

            response: Response = client.post(
                "/purchasePlaces",
                data={
                    "competition": "Invalid Competition",
                    "club": self.clubs[0]["name"],
                    "places": 1,
                },
            )
            assert response.status_code == 400
            assert b"Sorry, something went wrong. Please try again." in response.data

    def test_points_display_board_access_without_login(self):
        with app.test_client() as client:
            response: Response = client.get("/points")
            assert response.status_code == 200

    def test_points_access_with_login(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session["user"] = self.known_email
            response: Response = client.get("/points")
            assert response.status_code == 200

    def test_logout(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session["user"] = self.known_email
            response: Response = client.get("/logout", follow_redirects=True)
            assert response.status_code == 200
            assert b"Please enter your secretary email to continue" in response.data

    def test_index(self):
        with app.test_client() as client:
            response: Response = client.get("/")
            assert response.status_code == 200
            assert b"Please enter your secretary email to continue" in response.data

    def test_load_data_regular_config(self):
        with app.test_client():
            app.config["TESTING"] = False
            competitions, clubs = load_data()
            assert competitions is not None
            for competition in competitions:
                assert "test" not in competition["name"]
            assert clubs is not None
            for club in clubs:
                assert "test" not in club["name"]
            app.config["TESTING"] = True

    def test_book(self):
        with app.test_client() as client:
            # Test with a known competition and club
            competition = self.competitions[0]
            club = self.clubs[0]
            response = client.get(f"/book/{competition['name']}/{club['name']}")
            assert response.status_code == 200
            response_data = response.data.decode()
            assert f"Booking for {competition['name']}" in response_data

            # Test with an unknown competition or club
            response = client.get(f"/book/UnknownCompetition/{club['name']}")
            assert response.status_code == 400
            assert b"Something went wrong-please try again" in response.data

            response = client.get(f"/book/{competition['name']}/UnknownClub")
            assert response.status_code == 400
            assert b"Something went wrong-please try again" in response.data
