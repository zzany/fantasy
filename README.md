Team Defending Champions fantasy projection system. 

Borrows heavily from https://intoli.com/blog/fantasy-football-for-hackers/
	adapted to Python 2.7.x
	currently in the process of adapting to our auction style league

For use:
	update all fields that are idiosyncratic to our league (search for "to be updated")
	Scroll down to the bottom and read after "custom functions start here"

To do:
	pickle the scraping results so we don't have to rerun the scraper every time we want to run a function
	figure out why it thinks drew brees is better than everyone else... I think the points scoring is weird
	make a function that resolves our typed name to a best guess for player, e.g. "Drew Brees" should return "Brees, Drew"