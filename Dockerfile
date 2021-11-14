FROM python:3.9-slim
WORKDIR /slack-spotify-bot
ADD . /slack-spotify-bot
RUN pip install -r requirements.txt
EXPOSE 80 8080
ENTRYPOINT [ "python", "-m", "slack_spotify_bot" ]
CMD [ "dev" ]
