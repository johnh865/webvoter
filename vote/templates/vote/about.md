
WebVoter
========
**By John Huang**

Webvoter is a simple online tool to create polls and elections using a variety
of traditional and experimental voting methods. In additional to the traditional
"first-past-the-post", or plurality, voting method, Webvoter includes:

Ranked Ballot Methods
---------------------
Ranked methods rank candidates in order of most to least preferred. A sample ballot
for example is shown below: 

![Ranked ballot](../static/vote/ranking.png)

Ranked methods include:

  - [Instant runoff voting (IRV)](https://en.wikipedia.org/wiki/Instant-runoff_voting)
  - Top-two Automatic Runoff
  - Condorcet-compliant [Smith-minimax](https://electowiki.org/wiki/Smith//Minimax)
  - Condorcet-complaint [Ranked Pairs](https://en.wikipedia.org/wiki/Ranked_pairs)
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


Proportionate Representation Methods
------------------------------------
Several voting methods have been devised in order to construct
proportionate representation when selecting multiple winners. These methods include:

  - [Single transferable Vote](https://en.wikipedia.org/wiki/Single_transferable_vote)
  - [Reweighted Range Voting](https://electowiki.org/wiki/Reweighted_Range_Voting)
  - [Sequential Monroe Voting](https://electowiki.org/wiki/Sequential_Monroe_voting)


Source Code
-----------
Source code for the WebVoter webapp, as well as the voting engine, can be found 
on Github:

 - [votesim Python Package](https://github.com/johnh865/election_sim)
 - [Site source code](https://github.com/johnh865/webvoter)