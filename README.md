AI Agents for Settlers of Catan
CS221 Final Project, Fall 2014
By: Sherman Leung, Sierra Kaplan-Nelson, Nick Troccoli
---------------------------
We wrote a couple different agents for this assignment (all against the baseline Random agent).
These agents are: Expectimax, Expectiminimax, and Monte-Carlo Tree Search (MCTS).

By default, you can play the MCTS agent vs. random by running:
`python settlers.py`

To change the number of iterations played, use the `-n` flag and a number to specify the number you want.

To run the minimax agents, run
`python game.py -v`

Choose an Expectimax Agent (#11) or an Expectiminimax Agent (#12) from the game menu.

By default the depth is set to 1 and the number of iterations are set to 10. Use the `-d` and the `-n` flag respectively to change these values.

To turn off the turn-by-turn summary associated with the game, run:
`python game.py -m`

To view the graphics associated with the game,  add the -g flag.
