import requests
from discord import Webhook, RequestsWebhookAdapter
import time
import logging
import boto3
import json
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

logging.info('Initialising variables')

WEBHOOK_ID = os.getenv("WEBHOOK_ID")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")
BASEURL = 'https://api.opendota.com/api'
RECENT_MATCHES_ENDPOINT = '/players/{}/recentMatches'
HEROES_ENDPOINT = '/heroes'

rory_id = 1019180148
leigh_id = 180500608


def get_hero_name_from_id(id):
    logging.info('Getting hero name')
    heroes = requests.get(
        url=f'{BASEURL}{HEROES_ENDPOINT}'
    ).json()
    for hero in heroes:
        if hero['id'] == id:
            return hero['localized_name']


def get_time_since_match_end(start, duration):
    logging.info('Calculating time since last match')
    return (time.time() - (start + duration)) / 60


def get_last_match_info(player_id):
    logging.info('Retrieving last match data')
    last_match = requests.get(
        url=f'{BASEURL}{RECENT_MATCHES_ENDPOINT.format(player_id)}'
    ).json()[0]
    print(last_match)
    info_dict = {
        'win': (last_match['radiant_win'] is True and last_match['player_slot'] <= 5) or (
                last_match['radiant_win'] is False and last_match['player_slot'] > 5),
        'hero': get_hero_name_from_id(last_match['hero_id']),
        'time_since_match_end': get_time_since_match_end(last_match['start_time'], last_match['duration']),
        'deaths': last_match['deaths'],
        'match_id': last_match['match_id']
    }
    return info_dict


def get_s3_data():
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name='shamebot-match-id', key='data.json')
    data = json.loads(obj.get()['Body'].read())
    print(data)
    return data


def update_s3(match_id):
    data = {
        'last_match': match_id
    }
    with open('/tmp/data.json', 'w') as f:
        json.dump(data, f)
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(Filename='/tmp/data.json', Bucket='shamebot-match-id', Key='data.json')
    print('Upload to s3 successful')


def lambda_handler(event, context):
    try:
        logging.info('Starting lambda')
        match_dict = get_last_match_info(rory_id)
        s3_data = get_s3_data()

        print(match_dict)
        if not match_dict['win'] and match_dict['hero'] == 'Phantom Assassin' and match_dict['match_id'] != s3_data['last_match']:
            hero = match_dict['hero']
            deaths = match_dict['deaths']
            match_id = match_dict['match_id']
            # webhook set up
            webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
            webhook.send('Attention @everyone. Important announcement incoming.')
            time.sleep(10)
            webhook.send(
                f'Unforseeably, <@602469585467473921> lost a game as {hero}. Despite his best efforts he died {deaths} times. '
                f'Better luck next time!', username='Zayn Bot')
            webhook.send(f'https://www.dotabuff.com/matches/{match_id}')
            logging.info('Message successfully posted to discord')

            update_s3(match_id)
            return 'Finished'
    except Exception as e:
        logging.error(str(e))
        raise
    print('Lambda execution complete')
