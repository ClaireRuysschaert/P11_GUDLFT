from locust import HttpUser, between, task
from server import load_data

competitions, clubs = load_data()


class LocustWebsiteUser(HttpUser):
    wait_time = between(1, 5)
    competition = competitions[0]
    club = clubs[0]

    @task
    def index_login_logout(self):
        self.client.get("/")
        self.client.post(
            "/showSummary", data={"email": self.club["email"]},
            name="show_summary"
        )
        self.client.get("/logout")

    @task
    def view_board_club_point(self):
        self.client.get("/points")

    @task
    def get_booking(self):
        self.client.get(
            f"/book/{self.competition['name']}/{self.club['name']}",
            name="book"
        )

    @task
    def post_booking(self):
        self.client.post(
            "/purchasePlaces",
            data={
                "places": 0,
                "club": self.club["name"],
                "competition": self.competition["name"],
            },
            name="purchase_places",
        )
