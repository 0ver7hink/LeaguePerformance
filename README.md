# LeaguePerformance

The project went through a lot of changes, so it is possible that in near future will change also. But at the moment, program create a ranking for team and individual performance for League of Legends on ARAM gamemode only.

At now the program collects data about selected users and creates ranking for them, based on TrueSkill system. All of it will be available through web browser in the future (probably).

At the moment the program isn't prepared to be just downloaded and run easly.
When it will be ready, the instruction will be here.


But there is a feature that is worth mentioning.

For example, here is a screenshot from my terminal.
![image](https://github.com/0ver7hink/LeaguePerformance/assets/32736121/207ca336-7948-46e3-a736-32fa9aec86af)

It is the last match result.
First collumn informs if player was in team that wins (1) or lose (0).
second column is a percentage of probability of winning for each player - that rates individual performance, and that's where neural networks were implemented.

The idea of rating people in that way cames from my notice, that there are players that made their best and still lose. And of course, this error get lower the more games you play. but still think its worth to try different approach.

In LeaguePerformance that different approach is Winnable Impact (name of that parameter is still a work in progress), In screenshot above, player names Terr0rRoM scored the highest percentage of Winnable Impact despite he was in the loosing team. Normaly he would loose some ranking points, but in this universe, he will score the most because of his most positive impact on winning.

