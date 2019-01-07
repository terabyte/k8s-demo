FROM python:2

WORKDIR /usr/src/app
COPY persistence_server.py ./
EXPOSE 8080/tcp

CMD [ "python", "./persistence_server.py", "8080" ]

