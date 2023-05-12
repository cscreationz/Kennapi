import os
import discord
import spotipy
import spotipy.util as util
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging
logging.basicConfig(filename='discord_spotify.log', level=logging.ERROR)

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

voice_client = None

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    global voice_client
    
    if message.author == client.user:
        return

    if message.content.startswith('!play'):
        try:
            # Get the voice channel that the user is in
            channel = message.author.voice.channel
            if voice_client and voice_client.channel != channel:
                await voice_client.disconnect()
                voice_client = None
            if not voice_client:
                # Join the voice channel
                voice_client = await channel.connect()
                
            # Get the query and search for the track
            query = message.content.split(' ', 1)[1]
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                # Play the track in the voice channel
                voice_client.play(discord.FFmpegPCMAudio(executable='ffmpeg', source=sp.track(track_uri)['preview_url']))
                await message.channel.send(f'Now playing: {results["tracks"]["items"][0]["name"]}')
        except Exception as e:
            error_message = f'Error: Failed to play song: {e}'
            logging.error(error_message)
            await message.channel.send(error_message)

    elif message.content == '!stop':
        try:
            await voice_client.disconnect()
            voice_client = None
            await message.channel.send('Playback stopped')
        except Exception as e:
            error_message = f'Error: Failed to stop playback: {e}'
            logging.error(error_message)
            await message.channel.send(error_message)

    elif message.content == '!skip':
        try:
            sp.next_track()
            await message.channel.send('Skipped to the next song')
        except Exception as e:
            error_message = f'Error: Failed to skip to the next song: {e}'
            logging.error(error_message)
            await message.channel.send(error_message)

    elif message.content.startswith('!playlist'):
        try:
            playlist_uri = message.content.split(' ', 1)[1]
            sp.start_playback(context_uri=playlist_uri)
            await message.channel.send('Now playing playlist')
        except Exception as e:
            error_message = f'Error: Failed to play playlist: {e}'
            logging.error(error_message)
            await message.channel.send(error_message)

client.run(TOKEN)
