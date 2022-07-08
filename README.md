# Knoweldge Check

## Battleship Challenge

This challenge can be performed in pairs. Each one of you need to deploy a server that 
are able to communicate with each other.
Using your prefered programming language, create a battle board of 5x5 and include the 
location of 3 ships.
For each turn, each player should propose a coordinate that they think the other ship 
could be and update their grid map with their success or failures.

Example board:
```
Player 1                            ||  Player 2
===============================     ||  ===============================
\ 1      2      3      4      5     ||  \ 1      2      3      4      5
1 -      -      -      -      -     ||  1 -      -      -      -      -
2 -      -      -      -      -     ||  2 -      -      -      -      -
3 -      -      -      -      S     ||  3 -      -      -      -      -
4 -      -      S      -      -     ||  4 -      -      -      -      -
5 -      S      -      -      -     ||  5 -      -      -      -      -
```

For example here, we have a ship at 3:5, 4:3 and 5:2.

Try to send coordinates between each other until all ships have been downed. The 
symbols you can use can be:
```
S - ship is floating
@ - ship has been downed
* - miss
```

Battle Away !!!
