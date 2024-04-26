from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, flash, url_for


class Config(object):
    TESTING = False
    CLUBS_FILE = "clubs.json"
    COMPETITIONS_FILE = "competitions.json"


class TestConfig(object):
    TESTING = True
    CLUBS_FILE = "tests/clubs_test_data.json"
    COMPETITIONS_FILE = "tests/competitions_test_data.json"


app = Flask(__name__)
app.secret_key = "something_special"


def loadClubs():
    with open(app.config["CLUBS_FILE"]) as clubs_file:
        listOfClubs = json.load(clubs_file)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open(app.config["COMPETITIONS_FILE"]) as comps_file:
        listOfCompetitions = json.load(comps_file)["competitions"]
        return listOfCompetitions


def load_data():
    if app.config["TESTING"] == True:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    competitions = loadCompetitions()
    clubs = loadClubs()
    return competitions, clubs


def save_data(competitions, clubs):
    with open(app.config["COMPETITIONS_FILE"], "w") as comps_file:
        json.dump({"competitions": competitions}, comps_file)

    with open(app.config["CLUBS_FILE"], "w") as clubs_file:
        json.dump({"clubs": clubs}, clubs_file)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    competitions, clubs = load_data()
    try:
        form_email: str = request.form["email"]
        club = [club for club in clubs if club["email"] == form_email][0]
    except IndexError:
        if form_email == "":
            return (
                render_template(
                    "index.html", message="Please enter your email address"
                ),
                404,
            )
        else:
            return (
                render_template(
                    "index.html",
                    message="Sorry, we don't have your email address in our records. Please try again or contact the club.",
                ),
                404,
            )
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    competitions, clubs = load_data()
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    if foundClub and foundCompetition:
        return render_template(
            "booking.html", club=foundClub, competition=foundCompetition
        )
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competitions, clubs = load_data()
    try:
        competition = [
            compet
            for compet in competitions
            if compet["name"] == request.form["competition"]
        ][0]

        club = [club for club in clubs if club["name"] == request.form["club"]][0]

        desired_places = int(request.form["places"])
        club_points = int(club["points"])

        competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
        if competition_date < datetime.now():
            return (
                render_template(
                    "booking.html",
                    club=club,
                    competition=competition,
                    message="Sorry, this competition has already taken place.",
                ),
                400,
            )

        MAX_PLACES_ALLOWED_TO_PURCHASE = 12
        if desired_places > MAX_PLACES_ALLOWED_TO_PURCHASE:
            return (
                render_template(
                    "booking.html",
                    club=club,
                    competition=competition,
                    message="Sorry, you can't purchase more than 12 places at a time.",
                ),
                400,
            )

        if club_points < desired_places:
            return (
                render_template(
                    "booking.html",
                    club=club,
                    competition=competition,
                    message=f"Sorry, you don't have enough points to purchase {desired_places} places.",
                ),
                400,
            )

        if desired_places > int(competition["numberOfPlaces"]):
            return (
                render_template(
                    "booking.html",
                    club=club,
                    competition=competition,
                    message=f"Sorry, there are not enough places left in this competition to purchase {desired_places} places.",
                ),
                400,
            )

        club["points"] = str(club_points - desired_places)
        competition["numberOfPlaces"] = str(
            (int(competition["numberOfPlaces"]) - desired_places)
        )
        save_data(competitions, clubs)

        return render_template(
            "welcome.html",
            club=club,
            competitions=competitions,
            message="Great-booking complete!",
        )
    except IndexError as e:
        print("Error in purchasePlaces")
        for compet in competitions:
            print(f"compet = {compet}")
        print(f'competition form : {request.form["competition"]}')
        print(e)
        for club in clubs:
            print(f"club = {club}")
            print(f"club points : {club['points']}")


@app.route("/points")
def points():
    competitions, clubs = load_data()
    return render_template("club_points_board.html", clubs=clubs)

@app.route("/logout")
def logout():
    return redirect(url_for("index"))
