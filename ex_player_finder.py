from bs4 import BeautifulSoup
import requests
from multiprocessing.dummy import Pool
from functools import partial
from datetime import datetime, timedelta

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

def is_time_format(input):
    try:
        datetime.strptime(input, '%I:%M %p')
        return True
    except ValueError:
        return False

def used_to_play_for(team, player):
    if player=='':
        return False
    html = requests.get('https://www.transfermarkt.co.uk/player-name/transfers/spieler/{}'.format(player if player.isnumeric() else find_player(player)), headers=head)
    soup = BeautifulSoup(html.text, features='html.parser')
    try:
        ret = team.lower() in soup.find_all('tr', class_='zeile-transfer')[0].parent.get_text().lower()
    except:
        ret = False

    player_name = ''
    if ret:
        player_name = soup.title.text.replace(' - Transfer history | Transfermarkt','')
    return (player_name, ret)

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

def any_ex_players(team, match):
    plrz = get_players_involved(match)
    pool = Pool(4)
    func = partial(used_to_play_for, team)
    playersTF = pool.map(func, plrz)
    players = []
    
    for x in range(0, len(plrz)):
        if playersTF[x][1]:
            players.append(playersTF[x][0])
    return players

def fetch_current_matches():
    html = requests.get('https://www.transfermarkt.co.uk/ticker/index/live', headers=head)
    soup = BeautifulSoup(html.text, features='html.parser')
    home_tds = soup.find_all('td', class_='verein-heim')
    away_tds = soup.find_all('td', class_='verein-gast')
    all_matches = [(tr['id'], tr.find_all('span', class_='matchresult')[0].text) for tr in soup.find_all('tr', class_='begegnungZeile')]
    matches = []
    for match in all_matches:
        if is_time_format(match[1]):
            kick_off = datetime.strptime(match[1], '%I:%M %p')
            if datetime.now().time() >= (kick_off-timedelta(hours=1)).time():
                matches.append(match[0])
        else:
            matches.append(match[0])
    home = [td.find_all('a', class_='vereinprofil_tooltip')[0].text for td in home_tds]
    away = [td.find_all('a', class_='vereinprofil_tooltip')[1].text for td in away_tds]
    
    return list(zip(matches,(zip(home, away))))

def print_current_matches(matches):
    i=0
    for match in matches:
        i+=1
        print('{}. {} v {}'.format(i, match[1][0], match[1][1]))
    return matches

def check_match(match):
    all_ex_players = []
    ex_players = any_ex_players(team, match[0])
    if len(ex_players)>0:
        all_ex_players.append(('{} v {}: '.format(match[1][0], match[1][1]), ex_players))

    print('-', end='')
    return all_ex_players

matches = print_current_matches(fetch_current_matches())
choice = input('\nEnter match choice: (1-{} or type \'all\' for all matches)\n> '.format(len(matches)))
team = input('\nEnter a team: \n> ')

start_time = datetime.now()
if choice=='all':
    pool = Pool(4)
    all_ex_players = [x[0] for x in pool.map(check_match, matches) if len(x)>0]

    print('\n')
    total_players = 0
    for game in all_ex_players:
        total_players += len(game[1])
        print('\n{}{}'.format(game[0], ', '.join(game[1])))
    print('\nFound {} players in {}'.format(total_players, datetime.now() - start_time))
else:
    ex_players = any_ex_players(team, matches[int(choice)-1][0])
    print('\n'+str(ex_players)+'\nFound {} players in {}'.format(len(ex_players), datetime.now() - start_time))
