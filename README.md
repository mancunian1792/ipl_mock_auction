# ipl_mock_auction
Mock IPL auction.

### Context:
Most of my friends, including me, are interested in cricket. The corona crisis has made most of us bored during the weekends and we wanted a way to spend our time away. Few of them came up with an idea of holding a mock auction where they give a rating to each player based on stats in IPL( Indian Premiere League). This rating won't be revealed to anyone till the end. The idea is to have 8 teams (comprised of 3 people per team) put up a lineup of 11 players and the one with maximum rating wins.

### RULES:
1. Each team can only select 11 players.
2. Batsman - Min 3 Max 5
3. Bowlers - Min 3 Max 5
4. All Rounders - Min 1 Max 3
5. Wicketkeepers - 1
6. Max Spending limit - 30 crores.
7 . Overseas Players - 4

### PLAYERS CHOSEN:
Around 240 players , throughout the history of IPL, were chosen by them and a list was released indicating their roles(BAT/BOWL/ALLROUNDER/WK). The only clue about the rating that was given was that it was derived from stats in their own way

### IDEA:
Being a data scientist , it was right up my ally and i wanted to build a system that could help me in choosing the best players . 
1. **Scraping** -Scraped through the ipl website for stats of all the players from 2008-2019.
2. **Pre-Processing** - Created a heuristic rating from all the stats
3. **Optimization** -  Used **PuLP** package to solve an Binary Integer Programming optimization problem.
