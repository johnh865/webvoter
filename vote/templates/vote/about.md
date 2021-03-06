
WebVoter
========
**By John Huang**

Webvoter is a simple online tool to create polls and elections using a variety
of traditional and experimental voting methods using ranked or scored ballots.

Ranked Ballot Methods
---------------------
Ranked methods rank candidates in order of most to least preferred. A sample ballot
for example is shown below: 

![Ranked ballot](../static/vote/ranking.png)

Ranked methods include:

  - [Instant runoff voting (IRV)](https://en.wikipedia.org/wiki/Instant-runoff_voting)
  - Top-two Automatic Runoff
  - Condorcet-compliant methods:
    * [Ranked Pairs](https://en.wikipedia.org/wiki/Ranked_pairs)
    * [Smith-minimax](https://electowiki.org/wiki/Smith//Minimax)
    * [Black](https://en.wikipedia.org/wiki/Black%27s_method)
    * [Copeland](https://en.wikipedia.org/wiki/Copeland%27s_method)
  - [Borda Count](https://en.wikipedia.org/wiki/Borda_count)

Scored Ballot Methods
---------------------
Scoerd methods rate candidates from a scale. An example scored ballot is shown
below:

![Scored ballot](../static/vote/scoring.png)

Scored methods include:

  - [Scored voting](https://en.wikipedia.org/wiki/Score_voting)
  - [Majority judgment](https://en.wikipedia.org/wiki/Majority_judgment)
  - [Smith score](https://electowiki.org/wiki/Smith//Score)
  - [STAR voting (Score then Automatic Runoff)](https://en.wikipedia.org/wiki/STAR_voting)


Proportional Representation Methods
------------------------------------
Several voting methods have been devised in order to construct
proportionate representation when selecting multiple winners. These methods include:

  - [Single transferable Vote](https://en.wikipedia.org/wiki/Single_transferable_vote)
      * [Hare surplus allocation](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Hare)
      * [Gregory surplus allocation](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Gregory)
  - [Reweighted Range Voting](https://electowiki.org/wiki/Reweighted_Range_Voting)
  - [Sequential Monroe Voting](https://electowiki.org/wiki/Sequential_Monroe_voting)


Source Code
-----------
Source code for the WebVoter webapp, as well as the voting engine, can be found 
on Github:

 - [votesim Python Package](https://github.com/johnh865/election_sim)
 - [Site source code](https://github.com/johnh865/webvoter)