import os
import discord
import requests

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!track'):
        # Retrieve Wraithlander's summoner ID using Riot Games API
        response = requests.get('https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Wraithlander',
                                headers={'X-Riot-Token': os.environ['RIOT_API_KEY']})
        summoner_id = response.json()['id']

        # Retrieve Wraithlander's match history using Riot Games API
        response = requests.get(f'https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}?queue=420',
                                headers={'X-Riot-Token': os.environ['RIOT_API_KEY']})
        match_history = response.json()['matches']

        # Retrieve information about the last match
        response = requests.get(f'https://euw1.api.riotgames.com/lol/match/v4/matches/{match_history[0]["gameId"]}',
                                headers={'X-Riot-Token': os.environ['RIOT_API_KEY']})
        match_info = response.json()

        # Parse information about the last match
        champion_played = match_info['participantIdentities'][0]['player']['summonerName']
        result = 'Victory' if match_info['participants'][0]['stats']['win'] else 'Defeat'
        lp_gain = match_info['participants'][0]['stats']['leaguePoints']

        # Send a message to the channel with information about the last match
        await message.channel.send(f'Wraithlander just played {champion_played} and got {result} with {lp_gain} LP gain!')

client.run(os.environ['DISCORD_API_TOKEN'])