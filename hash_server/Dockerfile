FROM python:2

WORKDIR /usr/src/app
COPY hash_server.py ./
EXPOSE 8080/tcp

CMD [ "python", "./hash_server.py", "8080" ]

