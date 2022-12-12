from requests import get


apiurl = {
    'account': 'https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/',
    'matchlist': 'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/',
    'matchdata': 'https://europe.api.riotgames.com/lol/match/v5/matches/',
}
with open('token.md', 'r') as f:
        apitoken = f.read()

class Requester:
    def __init__(self):
        self.apitoken = apitoken


    def puuid(self, name='Norcia'):
        query = url['account'] + name + '?api_key=' + self.token
        response = get(query)
        if response.status_code == 200:
            return response.json()

        return
        
def getMatchIDs(self, puuid, count=1):
        q = url['matchlist'] + puuid + '/ids?start=0&count=' + str(count) + '&api_key=' + self.apitoken
        r = get(q)
        return r.json()

    def getmatch(self, matchid):
        q = url['matchdata'] + matchid + '?api_key=' + self.apitoken
        r = get(q)
        r = r.json()
        return r


    def extractDataFromMatch(self, match):
        participants = []
        thingstomeasure = [
                'puuid',
                'championName',
                'summonerName',
                'kills',
                'deaths',
                'assists',
                'damageDealtToObjectives',
                'teamId',
                'totalDamageDealtToChampions',
                'totalDamageShieldedOnTeammates',
                'totalHealsOnTeammates',
                'totalTimeCCDealt',
                ]
        self.thingstomeasure = thingstomeasure
        for i in match['info']['participants']:
            s = {}
            for thing in thingstomeasure:
                s[thing] = i[thing]
            participants.append(s)
        
        return participants


    def analyze(self, data):

        maximum = [] 
        minimum = []
        teamscore = {100: 0,200: 0}
        
        name = []
        score = []
        kda = []
        dmg = []
        obdmg = []
        cc = []
        killpart = []
        for i in data:
            name.append(i['championName'])
            i['score'] = i['kills'] + i['assists']
            score.append(i['kills']+i['assists'])
            kda.append(
                round((i['kills'] + i['assists']) / i['deaths'], 2)
                )
            dmg.append(
                i['totalDamageShieldedOnTeammates'] + 
                i['totalHealsOnTeammates'] + 
                i['totalDamageDealtToChampions']
                )
            obdmg.append(i['damageDealtToObjectives'])
            cc.append(i['totalTimeCCDealt'])
            teamscore[i['teamId']] += i['kills'] + i['assists']

        for i in data:
            killpart.append(
                round(i['score'] / teamscore[i['teamId']], 2)
                )

        for i in [kda, killpart, dmg, obdmg, cc]:
            i.append(max(i))
            i.append(min(i))

        points = []
        for i in range(10):
            x = []
            x.append(name[i])
            x.append(calc(i, kda))
            x.append(calc(i, killpart))
            x.append(calc(i, dmg))
            x.append(calc(i, obdmg))
            x.append(calc(i, cc))
            points.append(x)

        x = []
        for i in points:
            x.append([round(sum(i[1:]), 3), i])
        x.sort(key=lambda x: x[0])
        for i in x:
            print(i)

def lastMatchLeaderboard(self):
    identity = self.puuid()
    if identity:
        matchids = self.matchlist(identity['puuid'])
        matchid = matchids[0]
        match = self.getmatch(matchid)
        data = self.extractDataFromMatch(match)
        self.analyze(data)

def calc(pos, ar):
    return round((ar[pos] - ar[-1])/(ar[-2] - ar[-1]), 2)

#
# MAIN PROCEDURES
#

# Harvest: pozbieraj id ostatnich stu meczy uzytkowników kluczowych i zaimportuj do bazy danych, usun duplikaty nieocenionych meczy
    # SELECT puuid, name FROM user WHERE keyuser = 1;
    # wypisz nazwy userow kluczowych oraz ich liczbe w ostatnim wierszu
        # czy zatwierdzic?
            # exit: odrzucowo
            # return
    
    # clear
    # dla kazdego usera
        # pobierz n id meczy trybu aram
        # jezeli istnieje insert kazdego meczu do bazy danych z oznaczeniem przeanalizowania 0
        # wyswietl id wprowadzone/id odzucone

# Analyze: zacznij analize meczy w bazie danych, według kolejnoci id 
    # wez posortowane id meczy nieprzeanalizowanych
    # dla kazdego id
        # wyciahnij z serwerow riot games pelne dane meczu
        # opcjonalnie: wprowadz wszystkie dane do naszej bazy danych - o ile pamiec pozwoli - dla przyszlych projektow!
        # przeanalizuj
            # utworz obiekt gracze [puuid, [wszystkie potrzebne dane z meczu od riot], mu, sigma]
            # oblicz wskaznik istotnosci
            # posortuj obiekty
            # wprowadz zaktualizowane wartosci do trueskill
            # zaktualizowane wartosci wprowadz do bazy danych
                # zmien status przeanalizowanego meczu w bazie z 0 na 1
                # zaktualizj mu, sigme, matchcount
                    # gdy nie znajdzie gracza, ma go utworzyc z nowopowstanych danych

if __name__ == '__main__':
    summonerid = getSummonerIDByName("Norcia")
    match = getLastMatch(summonerId)
    Analyzer.launch(match)
            
