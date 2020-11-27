import requests
import time
import logging

BASEURL = 'https://api.opendota.com/api'
RECENT_MATCHES_ENDPOINT = '/players/{}/recentMatches'
HEROES_ENDPOINT = '/heroes'


class OpenDotaClient:
    def __get_time_since_match_end(self, start, duration):
        logging.info('Calculating time since last match')
        return (time.time() - (start + duration)) / 60

    def __determine_victory(self, radiant_win, player_slot):
        return (radiant_win is True and player_slot <= 5) or (radiant_win is False and player_slot > 5)

    def __get_hero_name_from_id(self, id):
        logging.info('Getting hero name')
        heroes = requests.get(
            url=f'{BASEURL}{HEROES_ENDPOINT}'
        ).json()
        for hero in heroes:
            if hero['id'] == id:
                return hero['localized_name']

    def get_last_match_info(self, player_id):
        logging.info('Retrieving last match data')
        last_match = requests.get(
            url=f'{BASEURL}{RECENT_MATCHES_ENDPOINT.format(player_id)}'
        ).json()[0]
        print(last_match)
        info_dict = {
            'win': self.__determine_victory(last_match['radiant_win'], last_match['player_slot']),
            'hero': self.__get_hero_name_from_id(last_match['hero_id']),
            'time_since_match_end': self.__get_time_since_match_end(last_match['start_time'], last_match['duration']),
            'deaths': last_match['deaths'],
            'match_id': last_match['match_id']
        }
        return info_dict