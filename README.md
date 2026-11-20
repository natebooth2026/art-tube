# Art Tube
Explore the art gallery using the secure web application

## Features
- Art gallery
- Sign ups and log ins
- Employee dashboard
- Admin dashboard
- viewing art gallery events

## Requirements
- Docker
- Python 3.14.8 (tested. earlier versions may work)

## Run with Docker

Docker runs MariaDB and phpMyAdmin. The Django application and
tests run locally.

1. Clone the repository and enter it:

        git clone https://github.com/natebooth2026/art-tube.git
        cd art-tube

2. Update `docker-compose.yml` with your username and password. Set `MARIADB_USER`, `MARIADB_PASSWORD`, and `MARIADB_ROOT_PASSWORD`.
   Update `.env` file in project root for Django with `DB_USER` and `DB_PWD` set
   to the same username and password.

3. Start MariaDB and phpMyAdmin:

        docker compose up -d

4. Create and activate a Python virtual environment from the repository root.
   On Linux/macOS:

        python3 -m venv .venv
        source .venv/bin/activate

   On Windows PowerShell:

        py -m venv .venv
        .venv\Scripts\Activate.ps1

5. Install the backend requirements: On Linux/macOS, first install the `libmagic`. `sudo apt install libmagic1` on Debian/Ubuntu or `brew install libmagic` on macOS.

        pip install -r src/backend/requirements.txt

6. Run migrations and start Django:

        cd src/backend
        python manage.py migrate
        python manage.py runserver_plus --cert-file cert.crt

7. Open the site at <https://127.0.0.1:8000/>.

## Run tests

1. From the repository root, open a MariaDB shell as root:

        docker compose exec db mariadb -u root -p

   Enter the `MARIADB_ROOT_PASSWORD` from `docker-compose.yml`, then
   run the SQL below. Replace `localhost` with your username
   `MARIADB_USER`:

        CREATE DATABASE IF NOT EXISTS test_secure_arttube;
        GRANT ALL PRIVILEGES ON test_secure_arttube.* TO 'localhost'@'%';
        EXIT;

2. From `src/backend`, run tests:

   Linux/macOS:

        PYTHONPATH=../../tests ../../.venv/bin/python manage.py test functional security --keepdb

   Windows PowerShell:

        $env:PYTHONPATH = "..\..\tests"
        python manage.py test functional security --keepdb

Stop the containers with `docker compose down`. Add `-v` only if you intend to
delete the database volume and all its data.

## Authors
Nate Booth\
Dylan Strnad
