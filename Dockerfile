# FROM python:3.8
# COPY ./requirements.txt /webapp/requirements.txt
# WORKDIR /webapp
# RUN pip install -r requirements.txt
# COPY webapp /webapp/
# EXPOSE 8000
# ENTRYPOINT [ "uvicorn" ]
# CMD ["--host", "0.0.0.0", "main:app"]

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
WORKDIR /webapp
COPY . /webapp
RUN pip install --upgrade pip &&\
   pip install --no-cache-dir --upgrade -r /webapp/requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]