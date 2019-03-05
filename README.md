# PyLette
The web-service for extracting dominant color from images.

![](https://pp.userapi.com/c848628/v848628718/134d9f/3akg9RQpsTs.jpg "Screenshot")

## Setup
1. Clone the repository: `git clone https://github.com/ViktorSalimonov/pylette.git`
2. Create a container: `docker-compose build`
3. Run the container: `docker-compose run`. To run multiple Celery workers: `docker-compose up --scale workers=N`

The application will be available on http://127.0.0.1:5000/
