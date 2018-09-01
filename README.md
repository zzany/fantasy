# Team Defending Champions fantasy projection system. 

Borrows heavily from https://intoli.com/blog/fantasy-football-for-hackers/

adapted to Python 2.7.x and to 2018

currently in the process of adapting to our auction style league

##For use:
	
update all fields that are idiosyncratic to our league (search for "to be updated")

Scroll down to the bottom and read after "custom functions start here"

##execute:

`python fantasy_scraper.py`

`python fantasy_analysis.py`

##To do:

Fix the aliasing/pointer problem between the players by name and players by id

make a function that resolves our typed name to a best guess for player, e.g. "Drew Brees" should return "Brees, Drew"
