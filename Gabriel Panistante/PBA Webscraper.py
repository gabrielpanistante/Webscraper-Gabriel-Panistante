import requests
from lxml import html
import os
import sys
from pandas import DataFrame
requests.packages.urllib3.disable_warnings()

headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
s = requests.Session()

def get_team_links():

    r_content = s.get('https://www.pba.ph/teams#', headers = headers, verify = False).content
    page = html.fromstring(r_content)
    
    return page.xpath('//*[contains(@class,"team-page-box")]//a/@href')

def get_teamname(team_url):
    r_content = s.get(team_url, headers = headers, verify = False).content
    page = html.fromstring(r_content)

    return page.xpath('//*[contains(@class,"team-profile-data")]//h3/text()')[0]
def get_headcoah(team_url):
    r_content = s.get(team_url, headers = headers, verify = False).content
    page = html.fromstring(r_content)
    
    return page.xpath('//*[contains(@class,"team-mgmt-header") and contains(.,"HEAD COACH")]//following-sibling::*[contains(@class,"team-mgmt-data")]/text()')[0]

def get_manager(team_url):
    r_content = s.get(team_url, headers = headers, verify = False).content
    page = html.fromstring(r_content)

    return page.xpath('//*[contains(@class,"team-mgmt-header") and contains(.,"MANAGER")]//following-sibling::*[contains(@class,"team-mgmt-data")]/text()')[0]

def get_logo(team_url):
    r_content = s.get(team_url, headers = headers, verify = False).content
    page = html.fromstring(r_content)

    return page.xpath('//*[contains(@class,"team-personal-bar")]//img/@src')[0]

def team_table():
    teams = get_team_links()
    team_data = []
    for team in teams:
        row = {}
        row['Team'] = get_teamname(team)
        row['Head Coach'] = get_headcoah(team)
        row['Manager'] = get_manager(team)
        row['URL'] = team
        row['Logo link'] = get_logo(team)
        team_data.append(row)

    return team_data

def player_table():
    r_content = s.get('https://www.pba.ph/players', headers = headers, verify = False).content
    page = html.fromstring(r_content)

    urls = page.xpath('//*[@class="playersBox"]/div[2]//@href')
    player_data = []
    for link in urls:
        
        player_content = s.get('https://www.pba.ph/'+link, headers = headers, verify = False).content
        player_page = html.fromstring(player_content)
        try:
            row = {}
            row['Team name'] = player_page.xpath('//*[@class="team-info color-tmc"]/text()')[0]
            row['Player name'] = player_page.xpath('//h3/text()')[0]
            row['Number'] = player_page.xpath('//*[@class="common-info"]/text()')[0].split(' / ',)[0].strip()
            row['Position'] = player_page.xpath('//*[@class="common-info"]/text()')[0].split(' / ')[-1].replace('/', ' ').strip()
            row['URL'] = link
            row['Mugshot'] = player_page.xpath('//*[contains(@class,"info-bar")]//@src')[0]
            player_data.append(row)
        except:
            pass

    return player_data


def csv_format(data):
    root_path = os.path.split(sys.argv[0])[0]
    if data == team_table():
        root_path = os.path.join(root_path, 'Team Data.csv')
    if data == player_table():
        root_path = os.path.join(root_path, 'Player Data.csv')
    df = DataFrame(data)
    df.to_csv(root_path, index = False)

def compile_data():
    data_type = [team_table(), player_table()]
    for data in data_type:
        csv_format(data)

if __name__ == '__main__':
    compile_data()