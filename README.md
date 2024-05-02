# P11 OpenClassrooms

1. Goal

The objectif is to improve an existing web application by optimizing code quality through testing and debugging.

In this project, my your mission is to improve the platform for booking places in strength competitions for the company Güdlft, developed with the Flask microframework.
The objective of the project is to fix errors and bugs present in the Python_Testing project, as well as to implement new features. Each fix/addition is on its own branch, and is supported by a test suite via Pytest and Locust.
I have fixed the bugs and implement feature from this repository: https://github.com/OpenClassrooms-Student-Center/Python_Testing/issues.

2. Why

    The demand is to create a lighter version of a flagship reservation system for organizers of local and regional competitions. This should allow the organizer to focus less on administration and more on the logistics of the competition, ensuring events are safe and efficient for everyone. The application will allow clubs to register athletes for competitions organized within the division.

3. Getting Started

    This project uses the following technologies:

    * Python v3.x+

    * [Flask](https://flask.palletsprojects.com/en/1.1.x/)

        Whereas Django does a lot of things for us out of the box, Flask allows us to add only what we need. 
     

    * [Virtual environment](https://virtualenv.pypa.io/en/stable/installation.html)

        This ensures you'll be able to install the correct packages without interfering with Python on your machine.

        Before you begin, please ensure you have this installed globally. 


4. Installation

    - After cloning <code>git clone https://github.com/ClaireRuysschaert/P11_GUDLFT.git</code>, change into the directory and type <code>virtualenv .</code>. This will then set up a a virtual python environment within that directory.

    - Next, type <code>source bin/activate</code>. You should see that your command prompt has changed to the name of the folder. This means that you can install packages in here without affecting affecting files outside. To deactivate, type <code>deactivate</code>

    - Rather than hunting around for the packages you need, you can install in one step. Type <code>pip install -r requirements.txt</code>. This will install all the packages listed in the respective file. If you install a package, make sure others know by updating the requirements.txt file. An easy way to do this is <code>pip freeze > requirements.txt</code>

    - Flask requires that you set an environmental variable to the python file, type <code>export FLASK_APP=server.py</code>

    - You should now be ready to test the application. In the directory, type either <code>flask run</code> or <code>python -m flask run</code>. The app should respond with an address you should be able to go to using your browser: http://127.0.0.1:5000/.

5. Current Setup

    The app is powered by [JSON files](https://www.tutorialspoint.com/json/json_quick_guide.htm). This is to get around having a DB until we actually need one. The main ones are:
     
    * competitions.json - list of competitions
    * clubs.json - list of clubs with relevant information. You can look here to see what email addresses the app will accept for login.

6. Testing

    I have used pytest run the tests, type <code>pytest tests</code>
    If you want to see the coverage, type <code>coverage run -m pytest tests</code>, then type <code>coverage report</code>.

7. Performance Test

It is possible to launch a performance test using the Locust module. To launch the test server, type <code>locust </code>.
Then, go to the address http://localhost:8089 and enter the desired options, with 'host' being the default address of the site (http://127.0.0.1:5000/).
