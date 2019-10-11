FROM python:3.7
WORKDIR /slack-spotify-bot
ADD . /slack-spotify-bot
RUN pip install -r requirements.txt
EXPOSE 80 8080
ENTRYPOINT [ "python", "main.py" ]
CMD [ "dev" ]
