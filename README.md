# PyLette
The web-service for extracting dominant color from images.

[Medium article](https://medium.com/@salimonov/%D0%B0%D1%81%D0%B8%D0%BD%D1%85%D1%80%D0%BE%D0%BD%D0%BD%D1%8B%D0%B5-%D1%84%D0%BE%D0%BD%D0%BE%D0%B2%D1%8B%D0%B5-%D0%B7%D0%B0%D0%B4%D0%B0%D0%BD%D0%B8%D1%8F-%D0%B2-flask-%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D0%B8-%D1%81-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5%D0%BC-celery-22c0dc9473ab) RU

[Medium article](https://medium.com/@salimonov/asynchronous-background-tasks-in-flask-application-using-celery-1ba873d260d0) EN

![](https://pp.userapi.com/c848628/v848628718/134d9f/3akg9RQpsTs.jpg "Screenshot")

## Setup
1. Clone the repository: `git clone https://github.com/ViktorSalimonov/pylette.git`
2. Create a container: `docker-compose build`
3. Run the container: `docker-compose run`. To run multiple Celery workers: `docker-compose up --scale worker=N`

The application will be available on http://127.0.0.1:5000/
