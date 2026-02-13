import re
import csv
import json
import logging
from logging.handlers import RotatingFileHandler
import playwright.sync_api
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Playwright
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from datetime import datetime

rootLink = "https://www.espn.com/nfl/teams"
#https://www.espn.com/nfl/teams

class PlayerRecord:
    def __init__(self, name='', date='',number=-1, team='', passyd=0,rushyd=0,recyd=0, opp='', pos=''):
        self.Name = name
        self.Date = date
        self.Number = number
        self.Team = team
        self.PassingYds = passyd
        self.RushingYds = rushyd
        self.ReceivingYds = recyd
        self.Opp = opp
        self.Pos = pos

#Years to read games from
targetYear = '2025'

# Test

logger  = logging.getLogger(__name__)
logging.basicConfig(filename="scraper.log", level=logging.INFO)

def normalize_date(date_str, year):
    # 'Sun 9/17' → '2025/9/17'
    cleaned = date_str.split()[1]
    full_date = f"{year}/{cleaned}"
    return datetime.strptime(full_date, "%Y/%m/%d").date()

def initCSV(filename='players.csv'):
    # Name, Num, Pos, Date, Opp, PassYd, RushYds
    headers = ['Team', 'Name', 'Number', 'Pos', 'Date', 'Opp', 'PassingYds', 'ReceivingYds', 'RushingYds']
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=headers)
        writer.writeheader()

def saveToCSV(data:PlayerRecord, filename='players.csv'):
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        headers = ['Team', 'Name', 'Number', 'Pos', 'Date', 'Opp', 'PassingYds', 'ReceivingYds', 'RushingYds']
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(data.__dict__)

def ValidateDate(date:str):
    dateformat = r'^[A-Za-z]+ \d{1,2}/\d{1,2}$'
    return bool(re.match(dateformat, date))

#region PlayerReading
def ReadQuarterBack(rows:playwright.sync_api.Locator, i:int, fullname:str, pos:str, number:int):
    curr = rows.nth(i).locator('td')
    Date = curr.nth(0).inner_text()

    if not ValidateDate(Date):
        logger.info('Not a game row')
        return None

    playerdata = []

    Opps = ''

    try:
        spanroot = curr.nth(1).locator('span')
        innerspan = spanroot.locator('span').nth(2)
        anchor = innerspan.locator('a')
        Opps = anchor.inner_text()
    except Exception as e:
        logger.info(f'Exception fetching Opponenets - {e}')
        Opps = 'N/A'

    PassYd = curr.nth(5).inner_text()
    RushYd = curr.nth(15).inner_text()

    playerdata.append({
        "Date": Date,
        "Opp": Opps,
        "PassYds": PassYd,
        "RushYds": RushYd,
        "Name": fullname,
        "Pos": pos,
        "Number": number
    })
    logger.info(f'{Date} | vs {Opps} - Passing:{PassYd} - Rushing:{RushYd}')
    return playerdata

def ReadRunningBack(rows:playwright.sync_api.Locator, i:int, fullname:str, pos:str, number:int):
    curr = rows.nth(i).locator('td')
    Date = curr.nth(0).inner_text()
    playerdata = []
    Opps = ''

    if not ValidateDate(Date):
        logger.info('Not a game row')
        return None

    try:
        spanroot = curr.nth(1).locator('span')
        innerspan = spanroot.locator('span').nth(2)
        anchor = innerspan.locator('a')
        Opps = anchor.inner_text()
    except Exception as e:
        logger.info(f'Exception fetching Opponenets - {e}')
        Opps = 'N/A'

    RushYd = curr.nth(4).inner_text()
    RecieveYd = curr.nth(10).inner_text()

    playerdata.append({
        "Date": Date,
        "Opp": Opps,
        "ReceiveYds": RecieveYd,
        "RushYds": RushYd,
        "Name": fullname,
        "Pos": pos,
        "Number": number
    })
    logger.info(f'{Date} | vs {Opps} - Receiving:{RecieveYd} - Rushing:{RushYd}')
    return playerdata

def ReadWideReciever(rows:playwright.sync_api.Locator, i:int, fullname:str, pos:str, number:int):
    curr = rows.nth(i).locator('td')
    Date = curr.nth(0).inner_text()
    playerdata = []
    Opps = ''

    if not ValidateDate(Date):
        logger.info('Not a game row')
        return None

    try:
        spanroot = curr.nth(1).locator('span')
        innerspan = spanroot.locator('span').nth(2)
        anchor = innerspan.locator('a')
        Opps = anchor.inner_text()
    except Exception as e:
        logger.info(f'Exception fetching Opponenets - {e}')
        Opps = 'N/A'

    RushYd = curr.nth(10).inner_text()
    RecieveYd = curr.nth(5).inner_text()

    playerdata.append({
        "Date": Date,
        "Opp": Opps,
        "ReceiveYds": RecieveYd,
        "RushYds": RushYd,
        "Name": fullname,
        "Pos": pos,
        "Number": number
    })
    logger.info(f'{Date} | vs {Opps} - Receiving:{RecieveYd} - Rushing:{RushYd}')
    return playerdata

def ReadTightEnd(rows:playwright.sync_api.Locator, i:int, fullname:str, pos:str, number:int):
    curr = rows.nth(i).locator('td')
    Date = curr.nth(0).inner_text()
    playerdata = []
    Opps = ''

    if not ValidateDate(Date):
        logger.info('Not a game row')
        return None

    try:
        spanroot = curr.nth(1).locator('span')
        innerspan = spanroot.locator('span').nth(2)
        anchor = innerspan.locator('a')
        Opps = anchor.inner_text()
    except Exception as e:
        logger.info(f'Exception fetching Opponenets - {e}')
        Opps = 'N/A'

    RushYd = curr.nth(4).inner_text()
    RecieveYd = curr.nth(10).inner_text()

    playerdata.append({
        "Date": Date,
        "Opp": Opps,
        "ReceiveYds": RecieveYd,
        "RushYds": RushYd,
        "Name": fullname,
        "Pos": pos,
        "Number": number
    })
    logger.info(f'{Date} | vs {Opps} - Receiving:{RecieveYd} - Rushing:{RushYd}')
    return playerdata

def ReadPlayerLog(rows:playwright.sync_api.Locator, i:int, fullname:str, pos:str, number:int) -> PlayerRecord:
    curr = rows.nth(i).locator('td')
    Date = curr.nth(0).inner_text()
    Opps = ''

    if not ValidateDate(Date):
        logger.info('Not a game row')
        return None

    try:
        spanroot = curr.nth(1).locator('span')
        innerspan = spanroot.locator('span').nth(2)
        anchor = innerspan.locator('a')
        Opps = anchor.inner_text()
    except Exception as e:
        logger.info(f'Exception fetching Opponenets - {e}')
        Opps = 'N/A'

    playerdata = None
    playerdata = PlayerRecord(name=fullname, date=Date, number=number, pos=pos, opp=Opps)

    if pos == 'QB':
        PassYd = curr.nth(5).inner_text()
        RushYd = curr.nth(15).inner_text()
        playerdata.PassingYds = PassYd
        playerdata.RushingYds = RushYd

    elif pos == 'RB':
        RushYd = curr.nth(4).inner_text()
        RecieveYd = curr.nth(10).inner_text()
        playerdata.RushingYds = RushYd
        playerdata.ReceivingYds = RecieveYd
    elif pos == 'WR':
        RushYd = curr.nth(10).inner_text()
        RecieveYd = curr.nth(5).inner_text()
        playerdata.RushingYds = RushYd
        playerdata.ReceivingYds = RecieveYd
    elif pos == 'TE':
        RushYd = curr.nth(4).inner_text()
        RecieveYd = curr.nth(10).inner_text()
        playerdata.RushingYds = RushYd
        playerdata.ReceivingYds = RecieveYd
    else:
        logger.info(f'Not recording position {pos}')
        return None

    return playerdata
#endregion

def GetPlayerGameData(page:playwright.sync_api.Page, link:str, pos:str, fullname, number, teamname):
    #https://www.espn.com/nfl/player/_/id/3918298/josh-allen
    #https://www.espn.com/nfl/player/gamelog/_/id/3918298/josh-allen

    gameUrl = link.replace('/player/', '/player/gamelog/')
    logger.info(gameUrl)
    page.goto(gameUrl)

    #Grab table div, Verify
    tableBase = page.locator('div[class*="gamelog"]').first
    if not tableBase.is_visible():
        logger.info('Table Base not found')
        return

    #Grab Regular Season table
    table = tableBase.locator('table').last
    if not table.is_visible():
        logger.info('Player has no data this season')
        return

    #Verify the player stats year
    yearheader = table.locator('thead').first
    yearrow = yearheader.locator('tr')
    year = yearrow.nth(0).locator('th').nth(0).inner_text()
    logger.info(f'year - {year}')
    if not year:
        logger.info('Can not validate player year')
        return
    elif targetYear not in year:
        logger.info('Player stats not current')
        return

    #Count the gamelog rows
    table = table.locator('tbody').last
    rows = table.locator('tr[class*="Table__TR"]:not([class*="totals_row"]):not([class*="Wrapper.Card__Content.NoDataAvailable__Content"])')
    count = rows.count()
    logger.info(f'rows: {count}')
    if count == 0:
        return

    data=[]
    positions = 'QB RB WR TE'

    #Get the last 3 played games
    for i in range(max(0, count-3), count):
        if pos in positions:
            data = ReadPlayerLog(rows, i, fullname, pos, number)

            if data is None:
                continue

            data.Team = teamname
            logger.info(f'{data.Date} {data.Name} {data.Number} vs {data.Opp} '
                  f'| Pos:{data.Pos} '
                  f'| Rush:{data.RushingYds} '
                  f'| Pass:{data.PassingYds} '
                  f'| Team:{data.Team} '
                  f'| Receive:{data.ReceivingYds}')

            refinedDate = normalize_date(data.Date, targetYear)

            # SAVE player data
            # saveToCSV(data)

            # STREAM to SPring HERE
            yield json.dumps({
                "team": data.Team,
                "name": data.Name,
                "number": data.Number,
                "position": data.Pos,
                "date": str(refinedDate),
                "opponent": data.Opp,
                "passingYds": data.PassingYds,
                "receivingYds": data.ReceivingYds,
                "rushingYds": data.RushingYds
            })+"\n"

        else:
            logger.info(f'Not recording position {pos}')
            return



# ^
# | Passes { Page, Link, "Position", Name, Number}
# |

def GoToPlayerPage(page: playwright.sync_api.Page, rowElement:playwright.sync_api.Locator, teamname:str):
    linkAnchor = rowElement.locator('td.Table__TD').nth(1).locator('a')
    if not linkAnchor.is_visible():
        logger.info('Player link not found')

    playerlink = linkAnchor.get_attribute('href')
    if not playerlink:
        logger.info('Player Link not found')
        return

    FullName = linkAnchor.inner_text()

    Numberspan = rowElement.locator('span')
    if not Numberspan.is_visible():
        logger.info('Player has no number')
        return

    Number = Numberspan.inner_text()
    Pos = rowElement.locator('td.Table__TD').nth(2).locator('div.inline').inner_text()
    # GetPlayerGameData(page, playerlink, Pos, FullName, Number, teamname)


    yield from GetPlayerGameData(page, playerlink, Pos, FullName, Number, teamname)

# ^
# | Passes { Page, row-element }
# |

def GoThroughRoster(page:playwright.sync_api.Page, link, tableName, teamname:str):
    page.goto(link)

    #Grabs the root div of a given list Offense/Defense
    table = page.locator(f'div.{tableName}').locator('tbody').first

    #Each row is a player
    playerlist = table.locator('tr[class*="Table__TR"]').all()

    for row in playerlist:
        # GoToPlayerPage(page, row, teamname)
        yield from GoToPlayerPage(page, row, teamname)

        #Route back to team home page
        page.goto(link)

# ^
# | Passes { Page, Roster Link, "Offense or Defense Table CSS-Class" }
# |

def DiveIntoTeam(browser: playwright.sync_api.Browser, teamLink:str, teamname:str):
    page = browser.new_page()
    newlink = urljoin(rootLink, teamLink)
    newlink = newlink.replace('/team/','/team/roster/')

    #Pass the roster link
    # GoThroughRoster(page, newlink, 'ResponsiveTable.Offense.Roster__MixedTable', teamname)
    yield from GoThroughRoster(page, newlink, 'ResponsiveTable.Offense.Roster__MixedTable', teamname)

    page.close()

# ^
# | Passes { Browser, Team Link }
# |

def Run(playwright: Playwright):
    # initCSV()
    logger.info("Scrape Started")

    chrome = playwright.chromium
    browser = chrome.launch()
    page = browser.new_page()

    page.goto(rootLink) #Route to Teams Page

    #Grab the division sections
    base = page.locator('div.Wrapper.TeamsWrapper')
    divisions = base.locator('.mt7').all()

    teamLinkStack = []

    #Gathers all the team links once
    for division in divisions:
        teamSection = division.locator('div.ContentList__Item').all()

        for team in teamSection:
            LinkB = team.locator('section.TeamLinks').locator('a.AnchorLink').first
            teamname = team.locator('section.TeamLinks').locator('h2').text_content()
            link = LinkB.get_attribute('href')
            teamLinkStack.append((link, teamname))

    #Go through each team link
    while len(teamLinkStack) > 0:
        link, teamname = teamLinkStack.pop()
        # DiveIntoTeam(browser, link, teamname)
        yield from DiveIntoTeam(browser, link, teamname)

    page.close()
    browser.close()
    logger.info("Scrape Finished")

def Environment():
    with sync_playwright() as playwright:
        # Run(playwright)
        yield from Run(playwright)

#Environment()

def yeildCheck():
    yield 1
    yield 2
    yield 3
    yield 4

#FastAPI---
app = FastAPI()

@app.get("/testEndpoint")
def root():
    yield from yeildCheck()

@app.get("/testPlayer")
def player():
    return {
    "team":"Chicago Bears",
    "name":"Caleb Williams",
    "number":18,
    "position":"QB",
    "date": "Thu/20",
    "opponent":"GB",
    "passingYds": 120.4,
    "receivingYds": 83,
    "rushingYds":14
    }

@app.get("/scrape")
def scrape():
    return StreamingResponse(Environment(), media_type="application/x-ndjson")

#test---
def testReadPlayer(link):
    with sync_playwright() as playwright:
        chrome = playwright.chromium
        browser = chrome.launch()
        page = browser.new_page()
        GetPlayerGameData(page, link, 'RB', 'TANK BIGSBY', '37')


#link = 'https://www.espn.com/nfl/player/_/id/4429013/tank-bigsby'
#testReadPlayer(link)