# FROM python:3.8
# COPY ./requirements.txt /webapp/requirements.txt
# WORKDIR /webapp
# RUN pip install -r requirements.txt
# COPY webapp /webapp/
# EXPOSE 8000
# ENTRYPOINT [ "uvicorn" ]
# CMD ["--host", "0.0.0.0", "main:app"]

# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
# WORKDIR /webapp
# COPY . /webapp
# RUN pip install --upgrade pip &&\
#    pip install --no-cache-dir --upgrade -r /webapp/requirements.txt
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

FROM public.ecr.aws/docker/library/python:3.11-bookworm

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Install uv for faster pip installs. See https://github.com/astral-sh/uv
RUN pip install uv

COPY requirements.txt /code/requirements.txt

RUN uv pip install --system -r /code/requirements.txt \
   uv cache clean

COPY ./app /code/app

WORKDIR /code/

RUN python -m app.preloader

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
