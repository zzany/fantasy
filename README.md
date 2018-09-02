# Team Defending Champions fantasy projection system. 

* Borrows heavily from https://intoli.com/blog/fantasy-football-for-hackers/
* adapted to Python 2.7.x and to 2018
* currently in the process of adapting to our auction style league

## For use:
	
* update all fields that are idiosyncratic to our league (search for "to be updated")
* Scroll down to the bottom and read after "custom functions start here"

## Execute:

`python fantasy_scraper.py`

`python fantasy_analysis.py`

Better yet, when it comes to draft day, open the python interpreter, type `execfile('fantasy_analysis.py')` then updated with league function calls as the draft happens

## To do:

* Create front-end to make interaction easier
* Make a function that returns many of the next most valuable players to a given team
* Make a function that returns many of the next most valuable players to a given team in a given position
* Make a function that given a player returns the value of that player to a given team and other players in the same position and their value
