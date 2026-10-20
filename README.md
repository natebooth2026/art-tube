# Art Tube
Explore the art gallery using the secure web application

## Features
- Art gallery
- Sign ups and log ins
- Employee dashboard
- Admin dashboard
- viewing art gallery events

## Requirements
- Python 3.14.8 (version tested)
- MySql or Mariadb

## Setup
1. clone the repository:
-  git clone https://github.com/natebooth2026/art-tube.git
2. create and activate .venv
    - linux/mac
        -  python3 -m venv .venv
        -  source .venv/bin/activate
    - windows
        -  py -m venv .venv
        -  .\.venv\Scripts\Activate.ps1
3. install dependencies:
    - pip install -r requirements.txt
4. connect to database:
    - create a new database in MySql called 'secure_arttube'
    - in art_tube/settings.py modify the following to inlcude username and password:
            DATABASES = {
                "default": {
                    "ENGINE": "django.db.backends.mysql", 
                    "NAME": "secure_arttube",
                    "USER": "mydatabaseuser",
                    "PASSWORD": "mypassword",
                    "HOST": "127.0.0.1",
                    "PORT": "3306",
                }
            }
5. apply database migrations
- python manage.py migrate
6. start server
- python manage.py runserver

## Usage
open http://127.0.0.1:8000/ in browser
