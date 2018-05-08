FROM python:3.6.5-slim

# install pipenv
RUN pip install pipenv

WORKDIR /usr/local/src/app

# copy app stuff
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY run.py run.py
COPY ./nccostorage ./nccostorage

# fetch deps
RUN pipenv install --deploy --system

EXPOSE 8080/tcp

CMD ["python", "run.py"]
