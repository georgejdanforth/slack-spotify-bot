# slack-spotify-bot
A self-hosted slack bot which collects shared Spotify links into a playlist. Built using [aiohttp](https://github.com/aio-libs/aiohttp).

## Setup Guide

### Prerequisites
To host this bot you will need
* Privileges to configure applications within your Slack workspace
* A Spotify developer account
* A hosting service (I deploy this on AWS)

### Spotify API setup

Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and create a new client ID. I just called mine "tunes bot

### Server Setup

1. SSH into the instance you want to deploy on. I use a free-tier AWS EC2 t2.nano running Amazon Linux 2 since it's the [easiest instance type to install Docker on](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html).
2. Make sure Docker is installed
3. Clone this repository and enter the newly created directory:
```
$ git clone https://github.com/georgejdanforth/slack-spotify-bot.git && cd slack-spotify-bot
```
4. Create a new config file:
```
$ cp example.config.json config.json
```
5. Using your `$EDITOR` of choice, open up `config.json` and populate the config parameters. The parameters are:
    * `server_domain`: Domain name or IP of the server hosting this service. Make sure to exclude `http://` from this. I just use my instance public IP for this parameter but if you'd like a proper domain name you're welcome to configure that yourself.
    * `slack_channel_id`: ID of the Slack channel to listen to for spotify links
    * `spotify_client_id`: Your Spotify API client ID
    * `spotify_client_secret`: Your Spotify API client secret
    * `spotify_playlist_id`: ID of the Spotify playlist to insert tracks into. This playlist should be owned by the same user holding the API credentials.

6. Create the Docker image:
```
sudo docker build -t slack-spotify-bot .
```
7. Run the Docker image:
```
docker run -p 8080:8080 -p 80:80 -d slack-spotify-bot prod
```

### Connecting to Spotify

1. After the server is set up, go back to the Spotify developer dashboard. Navigate to the Client ID you're using for this bot and click _Edit Settings_
2. Add `http://<your-server-ip-or-domain>/authorize/` to the redirect URIs and save
3. In your browser, navigate to `http://<your-server-ip-or-domain>/authorize/`. It should return a blank page with the text `Authorized!`

### Connecting to Slack

1. Go to https://api.slack.com/apps and click _Create New App_. Give the app a name (I called mine tunes-bot) and select the workspace you want to enable it in.
2. Enable _Event Subscriptions_. This should open up a new set of options.
3. Under _Request URL_, enter `http://<your-server-ip-or-domain>/`. It should validate automatically.
4. Add the `links_shared` workspace event
5. Add open.spotify.com as an _App Unfurl Domain_
6. Save changes
7. Navigate back to _Basic Information_ and install the app in your workspace.

You're all done! Posting Spotify links in the Slack channel specified by `slack_channel_id` should now add the tracks to the playlist specified by `spotify_playlist_id`.
