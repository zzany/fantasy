# -*- coding: future_fstrings -*-

# LEAGUE SETTINGS - TO BE UPDATED - be sure to also set starting positions for teams and number of teams

player_rules = {
    'pass yds': 0.04,  # Pass Yards
    'pass tds': 4,  # Pass Touchdowns
    'int': -2,  # Interceptions
    'rush yds': 0.1,  # Rush Yards
    'rush tds': 6,  # Rush Touchdowns
    'rec yds': 0.1,  # Reception Yards
    'rec tds': 6,  # Reception Touchdowns
    'fum': -2,  # Fumbles
    '10-19 fgm': 3,  # 10-19 Yard Field Goal
    '20-29 fgm': 3,  # 20-29 Yard Field Goal
    '30-39 fgm': 3,  # 30-39 Yard Field Goal
    '40-49 fgm': 3,  # 40-49 Yard Field Goal
    '50+ fgm': 5,  # 50+ Yard Field Goal
    'xpm': 1,  # Extra Point
}

team_rules = {
    'scks': 1,  # Sacks
    'int': 2,  # Interceptions
    'fum': 2,  # Fumbles
    'deftd': 6,  # Defensive Touchdowns
    'safts': 2,  # Safeties
}

# set up

def calculate_player_points(performance):
    points = 0
    for rule, value in player_rules.items():
        points += float(performance.get(rule, 0))*value
    return points


def calculate_team_points(performance):
    points = 0
    for rule, value in team_rules.items():
        points += float(performance[rule])*value

    # special brackets for "Points Against"
    points_against = float(performance['pts agn'])
    if points_against == 0:
        points += 10
    elif points_against < 7:
        points += 7
    elif points_against < 14:
        points += 2

    return points

def calculate_points(performance):
    if performance['position'] == 'D':
        return calculate_team_points(performance)
    return calculate_player_points(performance)    

from urllib2 import urlopen
import urllib2

def fetch_projections_page(week, position_id):
    assert 1 <= week <= 17, f'Invalid week: {week}'

    base_url = 'https://www.fantasysharks.com/apps/bert/forecasts/projections.php'
    url = f'{base_url}?League=-1&Position={position_id}&scoring=1&Segment={627 + week}&uid=4'

    request = urllib2.Request(url)
    request.add_header('User-Agent', 'projection-scraper 0.1')
    response = urlopen(request)
    return response.read()

import time

from bs4 import BeautifulSoup

def scrape_projections():
    for week in range(1, 17):
        position_map = { 'RB': 2, 'WR': 4, 'TE': 5, 'QB': 1, 'D': 6, 'K': 7 }
        for position, position_id in position_map.items():
            time.sleep(2)  # be polite
            html = fetch_projections_page(week, position_map[position])
            soup = BeautifulSoup(html, 'lxml')

            table = soup.find('table', id='toolData')
            header_row = table.find('tr')
            column_names = [th.text for th in header_row.find_all('th')]

            for row in table.find_all('tr'):
                column_entries = [tr.text for tr in row.find_all('td')]

                # exclude repeated header rows and the "Tier N" rows
                if len(column_entries) != len(column_names):
                    continue

                # extract Fantasy Shark's player id
                player_link = row.find('a')
                player_id = int(player_link['href'].split('=')[-1].strip())

                # yield a dictionary of this player's weekly projection
                player = { 'id': player_id, 'week': week, 'position': position }
                for key, entry in zip(column_names, column_entries):
                    player[key.lower()] = entry
                yield player


class Player:
    def __init__(self, id, position, name, team):
        self.id = id
        self.position = position
        self.name = name
        self.team = team
        self.points_per_week = [0]*18

    def add_projection(self, projection):
        assert self.id == projection['id']
        self.points_per_week[projection['week']] = calculate_points(projection)

    def season_points(self):
        return sum(self.points_per_week)

    def week_points(self, week):
        assert 1 <= week <= 17
        return self.points_per_week[week]
    def get_name(self):
    	return self.name

players_by_id = {}
players_by_name = {}
for projection in scrape_projections():
    player = players_by_id.get(projection['id'])
    if not player:
        player = Player(projection['id'], projection['position'], projection['player'], projection['tm'])
        players_by_id[projection['id']] = player
        players_by_name[projection['player']] = player
    player.add_projection(projection)

import pickle
file_players_by_id = open('filename_pi.obj', 'w')
pickle.dump(players_by_id, file_players_by_id)

file_players_by_name = open('filename_pn.obj', 'w')
pickle.dump(players_by_name, file_players_by_name)