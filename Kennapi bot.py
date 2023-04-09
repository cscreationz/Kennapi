import os
import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
redirect_uri = os.environ.get('REDIRECT_URI')
scope = 'user-read-playback-state,user-modify-playback-state'

bot = commands.Bot(command_prefix='!')

@bot.command()
async def play(ctx, *, song):
    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return
    else:
        channel = ctx.author.voice.channel
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))
    results = spotify.search(q=song, type='track', limit=1)
    uri = results['tracks']['items'][0]['uri']
    player = await channel.connect()
    player.play(discord.FFmpegPCMAudio(uri))
    await ctx.send(f"Now playing: {results['tracks']['items'][0]['name']}")

@bot.command()
async def stop(ctx):
    if not ctx.voice_client:
        await ctx.send("I am not connected to a voice channel.")
        return
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")

bot.run('your_bot_token')
