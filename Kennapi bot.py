import os
import discord
import spotipy
import spotipy.util as util
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SPOTIPY_USERNAME = os.getenv('SPOTIPY_USERNAME')

# Set up the Discord client and Spotify client
client = discord.Client()
scope = 'user-read-playback-state,user-modify-playback-state,user-read-private'
token = util.prompt_for_user_token(SPOTIPY_USERNAME, scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
sp = spotipy.Spotify(auth=token)


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!play'):
        try:
            query = message.content.split(' ', 1)[1]
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(uris=[track_uri])
                await message.channel.send(f'Now playing: {results["tracks"]["items"][0]["name"]}')
        except Exception as e:
            print(e)
            await message.channel.send('Error: Failed to play song')

    elif message.content == '!stop':
        try:
            sp.pause_playback()
            await message.channel.send('Playback stopped')
        except Exception as e:
            print(e)
            await message.channel.send('Error: Failed to stop playback')

    elif message.content == '!skip':
        try:
            sp.next_track()
            await message.channel.send('Skipped to the next song')
        except Exception as e:
            print(e)
            await message.channel.send('Error: Failed to skip to the next song')

    elif message.content.startswith('!playlist'):
        try:
            playlist_uri = message.content.split(' ', 1)[1]
            sp.start_playback(context_uri=playlist_uri)
            await message.channel.send('Now playing playlist')
        except Exception as e:
            print(e)
            await message.channel.send('Error: Failed to play playlist')

client.run(TOKEN)
