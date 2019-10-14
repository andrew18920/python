from bs4 import BeautifulSoup
import requests
from multiprocessing.dummy import Pool
from functools import partial
import datetime

head = {
    'Host':'www.transfermarkt.co.uk',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
}

def used_to_play_for(team, player):
    if player=='':
        return False
    html = requests.get('https://www.transfermarkt.co.uk/player-name/transfers/spieler/{}'.format(player if player.isnumeric() else find_player(player)), headers=head)
    soup = BeautifulSoup(html.text, features='html.parser')
    try:
        return team.lower() in soup.find_all('tr', class_='zeile-transfer')[0].parent.get_text().lower()
    except:
        return False

def find_player(name):
    html = requests.get('https://www.transfermarkt.co.uk/schnellsuche/ergebnis/schnellsuche?query={}'.format(name), headers=head)
    soup = BeautifulSoup(html.text, features='html.parser')
    return soup.find_all('a', class_='spielprofil_tooltip')[0]['id']

def get_players_involved(match):
    html = requests.get('https://www.transfermarkt.co.uk/ticker/begegnung/live/{}'.format(match), headers=head)
    soup = BeautifulSoup(html.text, features='html.parser')
    starters = [plr['id'] for plr in soup.find_all('span', class_='aufstellung-rueckennummer-name')]
    subs = [plr['id'] for plr in soup.find_all('td', class_='aufstellung-rueckennummer-ersatzbank')]
    return starters+subs

def get_player_name(player):
    html = requests.get('https://www.transfermarkt.co.uk/player-name/transfers/spieler/{}'.format(player), headers=head)
    soup = BeautifulSoup(html.text, features='html.parser')
    return soup.title.text.replace(' - Transfer history | Transfermarkt','')

def any_ex_players(team, match):
    plrz = get_players_involved(match)
    pool = Pool(4)
    func = partial(used_to_play_for, team)
    playersTF = pool.map(func, plrz)
    players = []
    
    for x in range(0, len(plrz)):
        if playersTF[x]:
            players.append(get_player_name(plrz[x]))
    return players

#def any_ex_players(team, match):
#    plrz = get_players_involved(match)
#    players = []
#    for player in plrz:
#        if used_to_play_for(team, player):
#            players.append(get_player_name(player))
#    return players

def fetch_current_matches():
    # $('.begegnungZeile')
    html = requests.get('https://www.transfermarkt.co.uk/ticker/index/live', headers=head)
    soup = BeautifulSoup(html.text, features='html.parser')
    home_tds = soup.find_all('td', class_='verein-heim')
    away_tds = soup.find_all('td', class_='verein-gast')
    matches = [tr['id'] for tr in soup.find_all('tr', class_='begegnungZeile')]
    home = [td.find_all('a', class_='vereinprofil_tooltip')[0].text for td in home_tds]
    away = [td.find_all('a', class_='vereinprofil_tooltip')[1].text for td in away_tds]

    return list(zip(matches,(zip(home, away))))

def print_current_matches(matches):
    i=0
    for match in matches:
        i+=1
        print('{}. {} v {}'.format(i, match[1][0], match[1][1]))
    return matches

matches = print_current_matches(fetch_current_matches())
choice = input('\nEnter match choice: (1-{} or type \'all\' for all matches)\n> ').format(len(matches))
team = input('\nEnter a team: \n> ')

if choice=='all':
    # Could make this bit concurrent/threaded
    all_ex_players = []
    for match in matches:
        ex_players = any_ex_players(team, match[0])
        if len(ex_players)>0:
            all_ex_players.append(('{} v {}: '.format(match[1][0], match[1][1]), ex_players))

    print('\n')
    for game in all_ex_players:
        print('{}{}'.format(game[0], ', '.join(game[1])))
else:
    print('\n'+str(any_ex_players(team, matches[int(choice)-1][0])))
