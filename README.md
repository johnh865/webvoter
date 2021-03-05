Webvoter
========
Webvoter is a Python django app written in Python 3.9.


Getting Started
---------------
To install the needed packages, run

	pip install -r requirements.txt

Now some commands need to be run to initialize
the app. 

	python manage.py makemigrations
	python manage.py migrate
	python manage.py gen_data


You also need to create a `.env` file in the app root folder and set a secret key:

    SECRET_KEY = 'THIS IS MY SECRET KEY' > .env


To run the django app on your local machine, use command:

	python manage.py runserver
	
Environmental Variables
-----------------------
- SECRET_KEY -- Django secret key.
- DEBUG -- Set DEBUG=1 for debug mode.
- HEROKU -- Set HEROKU=1 to use Heroku postgres database, which is needed to Heroku deployment. 


Deployment / Installation Guides
--------------------------------
* Getting Heroku to work: https://devcenter.heroku.com/articles/getting-started-with-python
* Getting Postgres to work on Heroku: https://devcenter.heroku.com/articles/heroku-postgresql
* Postgres Windows installer: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
