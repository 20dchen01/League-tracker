import os
import requests
import discord
from discord.ext import tasks

client = discord.Client()

# Replace with your own Riot Games API key
RIOT_API_KEY = os.environ['RIOT_API_KEY']
# Replace with your own Discord API key
DISCORD_API_KEY = os.environ['DISCORD_API_KEY']

# The summoner name and region to track
summoner_name = "Wraithlander"
region = "euw1"

# The ID of the channel to post updates in
channel_id = 1234567890

@tasks.loop(minutes=1)
async def track_ranked_games():
    try:
        # Get summoner data
        summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
        summoner_data = requests.get(summoner_url, headers={"X-Riot-Token": RIOT_API_KEY}).json()
        summoner_id = summoner_data['id']

        # Get match history
        match_history_url = f"https://{region}.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}?queue=420"
        match_history_data = requests.get(match_history_url, headers={"X-Riot-Token": RIOT_API_KEY}).json()
        match_id = match_history_data['matches'][0]['gameId']

        # Get match data
        match_url = f"https://{region}.api.riotgames.com/lol/match/v4/matches/{match_id}"
        match_data = requests.get(match_url, headers={"X-Riot-Token": RIOT_API_KEY}).json()
        participant_id = -1
        for i in range(len(match_data['participantIdentities'])):
            if match_data['participantIdentities'][i]['player']['summonerName'] == summoner_name:
                participant_id = match_data['participantIdentities'][i]['participantId']
                break
        stats = match_data['participants'][participant_id - 1]['stats']
        result = "Victory" if stats['win'] else "Defeat"
        lp_gain = stats['win'] * (int(match_data['gameDuration']) // 60 + 3)

        # Get champion data
        champion_url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}"
        champion_data = requests.get(champion_url, headers={"X-Riot-Token": RIOT_API_KEY}).json()
        champion_id = match_data['participants'][participant_id - 1]['championId']
        champion_name = ""
        for champion in champion_data:
            if champion['championId'] == champion_id:
                champion_name = champion['championName']
                break

        # Post update in Discord channel
        channel = client.get_channel(channel_id)
        message = f"{summoner_name}'s last ranked game:\nResult: {result}\nLP gain: {lp_gain}\nChampion played: {champion_name}"
        await channel.send(message)

    except Exception as e:
        print(f"Error tracking ranked games: {e}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    track_ranked_games.start()

client.run(DISCORD_API_KEY)