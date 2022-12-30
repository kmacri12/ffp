import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment

def get_playoffs_teams_list():
    playoffs_url = 'https://www.pro-football-reference.com/years/2022/playoffs.htm'
    page = requests.get(playoffs_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    teams_list = []
    for i in range(1,8):
        for conf in ['afc', 'nfc']:
            link = soup.select(f'#{conf}_playoffs > tbody > tr:nth-child({i}) > td.left > a')[0].get('href')
            team_abbr = link.split('/')[2]
            teams_list.append(team_abbr)
    return teams_list
    

def get_teams():
    playoffs_url = 'https://www.pro-football-reference.com/years/2022/playoffs.htm'

    dfs = pd.read_html(playoffs_url)
    nfc = dfs[0]
    nfc_teams = nfc.head(7)
    afc = dfs[1]
    afc_teams = afc.head(7)
    return (nfc_teams, afc_teams)

def get_players_for_team(team_abbr):
    response = requests.get(f'https://www.pro-football-reference.com/teams/{team_abbr}/2022_roster.htm')

    soup = BeautifulSoup(response.text, 'html.parser')
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    players = []
    positions = ['QB', 'RB', 'WR', 'TE', 'K']
    for each in comments:
        if 'table' in each:
            try:
                comment_soup = BeautifulSoup(each, 'html.parser')
                table = comment_soup.find("table")
                tbody = table.find('tbody')
                rows = tbody.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    for item in cols:
                        header = item.attrs['data-stat']
                        if header == 'player':
                            player_id = item.attrs['data-append-csv']
                    cols = [ele.text.strip() for ele in cols]
                    name = cols[0]
                    pos = cols[2]
                    pos = 'RB' if pos == 'FB' else pos
                    player = {'name': name, 'pos': pos, 'player_id': player_id, 'team': team_abbr}
                    if pos in positions:
                        players.append(player)

            except:
                continue
    return players

def get_all_draftable_players():
    teams = get_playoffs_teams_list()
    player_list = []
    for team in teams:
        players = get_players_for_team(team)
        player_list = player_list + players
    player_list = sorted(player_list, key=lambda d: d['name'])
    return player_list

def print_draft_list(players):
    for player in players:
        name = player['name'].split('(IR)')[0].strip()
        name = name.split('(IRD)')[0].strip()
        team = player['team'].upper()
        team = 'LAC' if team == 'SDG' else team
        team = 'BAL' if team == 'RAV' else team
        team = 'SF' if team == 'SFO' else team
        team = 'TB' if team == 'TAM' else team
        pos = player['pos']
        line = f'{name} ({team}) {pos}'
        print(line)

if __name__ == '__main__':
    draftable_players = get_all_draftable_players()
    print_draft_list(draftable_players)