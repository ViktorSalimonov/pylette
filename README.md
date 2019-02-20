# PyLette
The web-service for extracting dominant color from images.

![](https://pp.userapi.com/c848628/v848628718/134d9f/3akg9RQpsTs.jpg "Screenshot")

## Setup
1. Clone the repository: `git clone https://github.com/ViktorSalimonov/pylette.git`
2. Install a virtualenv in the `pylette` directory: `virtualenv venv`
3. Activate it: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Lauch celery in the `app` directory: `celery -A app.celery worker --loglevel=info`
6. Run the server in another terminal (don't forget to activate virtual environment): `python app.py`

The application will be available on http://127.0.0.1:5000/
