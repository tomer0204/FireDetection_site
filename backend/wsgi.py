from app import create_app
# to run development server write and activate .venv run the command in the folder FireDetection_site -
# source .venv/bin/activate && cd backend && FLASK_APP=wsgi.py FLASK_ENV=development flask run
app = create_app()

if __name__ == "__main__":
    app.run()
