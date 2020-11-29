import json
import requests
import datetime
import flag

from config import CoronaLiveAPI


class Sentence:
    def fluctuation_value(self, current_value, fluct_value):
        """
            : value of increase compared to yesterday
            : ex) today_infected = 100, compared_value = -10
            : ex) result: increase compared to yesterday: ▼10
        """
        value = f"{current_value:,}"
        if fluct_value == 0:
            return f"{value} ( - )"
        elif fluct_value < 0:
            return f"{value} (▼ {fluct_value:,})"
        else:
            return f"{value} (▲ {fluct_value:,})"
    
    def infected(self, now, fluct_value):
        return f"🥵 {self.fluctuation_value(now, fluct_value)}"
        
    def deceased(self, now, fluct_value):
        return f"☠️ {self.fluctuation_value(now, fluct_value)}"
        
    def recovered(self, now, fluct_value):
        return f"🌡 {self.fluctuation_value(now, fluct_value)}"
          

class CoronaLive:
    def __init__(self):
        self.api = CoronaLiveAPI()
        self.sentence = Sentence()
        self._set_infected_data()
    
    def _set_infected_data(self):
        world = requests.get( self._get_url('world') )
        self.world = world.json()['stats']
        self.world_idx = 0
        for index, key_name in enumerate(self.world.keys()):
            if key_name == 'WORLD':
                self.world_idx = index
    
    def _get_url(self, uri):
        return self.api.CORONA_LIVE_URL + self.api.URI[uri]

    def korea_status(self):
        korea = self.world["KR"]
        now = requests.get( self._get_url('stats') )
        now = now.json()['overview']

        lines = [
            "* 🇰🇷 South Korea COVID-19 Status *",
            "* Total *",
            f"  - 🥵 {korea['cases']:,} (▲ {korea['casesDelta']:,})",
            f"  - ☠️ {korea['deaths']:,} (▲ {korea['deathsDelta']:,})",
            "* Real Time * (Compared to yesterday)",
            f"  - {self.sentence.infected(*now['current'])}",
        ]
        return lines

    def world_top10_status(self):
        lines = []
        for index, country in enumerate(self.world):
            if index > self.world_idx and index < self.world_idx + 11:
                cvalue = self.world[country]
                rank = str(index - self.world_idx)
                line = f"#{rank} " if len(rank)==2 else f"#{rank}  "
                line += f"{flag.flag(country)} {country}: 🥵 {cvalue['cases']:,} (▲ {cvalue['casesDelta']:,})"
                lines.append(line)
        return lines

    def world_status(self):
        world = self.world['WORLD']
        return [
            "* 🌏 World COVID-19 Status *",
            f"  - 🥵 {world['cases']:,} (▲ {world['casesDelta']:,})",
            f"  - ☠️ {world['deaths']:,} (▲ {world['deathsDelta']:,})",
            "\n"
        ]
    
    def last_updated_at(self):
        ts = requests.get( self._get_url('updated_at') ).text
        dt = datetime.datetime.fromtimestamp(int(ts)/ 1e3)
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} (UTC +0900)"

    def generate_message(self):
        message = "\n".join(self.korea_status())
        message += ("\n" + "--" * 20 + "\n")
        message += "\n".join(self.world_status())
        message += "\n".join(self.world_top10_status())
        message += ("\n\n``` Last Updated: " + self.last_updated_at() + " ```")
        return message