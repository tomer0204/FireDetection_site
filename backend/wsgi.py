# to run development server write and activate .venv run the command in the folder FireDetection_site -
# source .venv/bin/activate  && FLASK_APP=wsgi.py FLASK_ENV=development flask run
from app import create_app

flask_app = create_app()

if __name__ == "__main__":
    flask_app.run()
