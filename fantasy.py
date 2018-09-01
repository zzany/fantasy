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
    url = f'{base_url}?League=-1&Position={position_id}&scoring=1&Segment={595 + week}&uid=4'

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

# To be updated based on league rules
class Team:
    allowed_flex_positions = ['RB', 'TE', 'WR']
    maximum_players = 18
    starting_positions = ['K', 'D', 'FLEX', 'QB', 'RB', 'RB', 'TE', 'WR', 'WR']
    weeks = list(range(1, 17))

    def __init__(self):
        self.players_by_id = {}

    def add_player(self, player):
        assert self.player_count() < self.maximum_players
        self.players_by_id[player.id] = player

    def remove_player(self, player):
        del self.players_by_id[player.id]

    def clear_players(self):
        self.players_by_id = {}

    def players(self):
        return self.players_by_id.values()

    def player_count(self):
        return len(self.players_by_id)

    def team_full(self):
        return self.player_count() == self.maximum_players

    def starters(self, week):
        remaining_players = sorted(self.players_by_id.values(),
                         key=lambda player: player.week_points(week), reverse=True)
        starters = []
        flex_count = 0
        for position in self.starting_positions:
            # we'll handle flex players later
            if position == 'FLEX':
                flex_count += 1
                continue
            # fnd the best player with this position
            for i, player in enumerate(remaining_players):
                if player.position == position:
                    starters.append(player)
                    del remaining_players[i]
                    break

        # do the same for flex players
        for i in range(flex_count):
            for j, player in enumerate(remaining_players):
                if player.position in self.allowed_flex_positions:
                    starters.append(player)
                    del remaining_players[j]

        return starters

    def season_points(self):
        return sum((self.week_points(week) for week in self.weeks))

    def week_points(self, week):
        return sum((player.week_points(week) for player in self.starters(week)))

from collections import defaultdict
import random

#number of teams to be updated
class League:
    number_of_teams = 12
    team_class = Team

    def __init__(self, players):
        self.teams = [self.team_class() for i in range(self.number_of_teams)]
        self.all_players = [player for player in players]
        self.available_players = [player for player in players]


    def clear_teams(self):
        self.available_players = [player for player in self.all_players]
        for team in self.teams:
            team.clear_players()

    def calculate_baselines(self):
        projections = defaultdict(list)
        for player in self.available_players:
            points = sum((player.week_points(week) for week in self.teams[0].weeks))
            projections[player.position].append(points)
        return { position: max(points) for position, points in projections.items() }

    def optimize_teams(self, same_positions=False):
        # cycle through and pick up available players
        optimal = False
        trades = 0
        while not optimal:
            optimal = True
            for team in sorted(self.teams, key=lambda t: random.random()):
                for original_player in list(team.players()):
                    # find the best trade with available players
                    original_points = team.season_points()
                    team.remove_player(original_player)
                    best_player, best_points = original_player, original_points
                    for new_player in self.available_players:
                        if same_positions and new_player.position != original_player.position:
                            continue
                        # don't bother computing if the new player is strictly worse
                        if new_player.position == original_player.position:
                            for week in team.weeks:
                                if new_player.week_points(week) > original_player.week_points(week):
                                    break
                            else:
                                # strictly worse
                                continue

                        team.add_player(new_player)
                        new_points = team.season_points()
                        if new_points > best_points:
                            best_points = new_points
                            best_player = new_player
                        team.remove_player(new_player)

                    # update the team if an available player is better
                    if best_player != original_player:
                        optimal = False
                        trades += 1
                        self.available_players.append(original_player)
                        self.available_players.remove(best_player)
                        team.add_player(best_player)
                    else:
                        team.add_player(original_player)

    def fill_teams_greedily(self):
        self.clear_teams()
        for i in range(self.team_class.maximum_players):
            for team in sorted(self.teams, key=lambda t: random.random()):
                best_player, best_points = None, None
                for new_player in self.available_players:
                    team.add_player(new_player)
                    new_points = team.season_points()
                    if not best_player or new_points > best_points:
                        best_points = new_points
                        best_player = new_player
                    team.remove_player(new_player)
                team.add_player(best_player)
                self.available_players.remove(best_player)

    def randomize_teams(self):
        self.clear_teams()
        for team in self.teams:
            while not team.team_full():
                index = random.randint(0, len(self.available_players) - 1)
                team.add_player(self.available_players.pop(index))

    def set_weeks(self, weeks):
        for team in self.teams:
            team.weeks = weeks

#custom functions start here:

    def optimize_team(self):
    	our_team = self.teams[0]
    	best_player, best_points = None, None
        for new_player in self.available_players:
            our_team.add_player(new_player)
            new_points = our_team.season_points()
            if not best_player or new_points > best_points:
                best_points = new_points
                best_player = new_player
            our_team.remove_player(new_player)
        return best_player.get_name()

    def assign_player(self, player_name, team_number):
    	new_team = self.teams[team_number]
    	drafted_player = players_by_name.get(player_name)
    	new_team.add_player(drafted_player)
    	self.available_players.remove(drafted_player)

    def add_player_to_our_team(self, player_name):
    	drafted_player = players_by_name.get(player_name)
    	our_team = self.teams[0]
    	our_team.add_player(drafted_player)
    	self.available_players.remove(drafted_player)

    def value_to_team(self, player_name, team_number):
    	team = self.teams[team_number]
    	new_player = players_by_name.get(player_name)
    	old_points = team.season_points()
    	team.add_player(new_player)
        new_points = team.season_points()
        team.remove_player(new_player)
        return new_points - old_points

    def value_of_player(self, player_name):
    	value_by_team = []
    	new_player = players_by_name.get(player_name)
        for team in self.teams:
            old_points = team.season_points()
            team.add_player(new_player)
            new_points = team.season_points()
            team.remove_player(new_player)
            value_by_team.append(new_points - old_points)
    	return value_by_team    		
		
# populate the teams and bring them to equilibrium
league = League(players_by_id.values())

# player remaining with most value to us
print league.optimize_team()

# do to determine value of player currently up for auction
print league.value_of_player("Brees, Drew")

# do once someone purchases a player
print league.assign_player("Brees, Drew", 0)


#league.fill_teams_greedily()
#league.optimize_teams()

# calculate the waiver wire baselines
#baselines = league.calculate_baselines()