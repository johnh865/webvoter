
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

  - **[Instant runoff voting (IRV)](https://en.wikipedia.org/wiki/Instant-runoff_voting)** - 
    Also known as "Ranked Choice Voting", instant runoff allows voters to rank candidates from first to last. 
    To select the winner, instant runoff eliminates candidates one-by-one based on who receives the fewest top-choice votes.
    The eliminated candidate's votes are then added to the total of their next choice.

  - **Top-two Automatic Runoff** - In top two runoff, the winner is determined from two-rounds of voting. 
    The first round eliminates all but two candidates. The second round then determines the winner from the final two winners.
    Webvoter simulates runoffs using ranked ballots to compare preferences. 

  - **Condorcet-compliant methods** - Condorcet methods are a family of voting systems that allow voters
    to rank candidates from first to last. To select the winner, Condorcet methods simulate multiple head-to-head elections. 
    The Condorcet criterion proposes that the best candidate is the candidate which can win every single 1 vs 1 election combination.
    Take for example a three-way election with candidates Washington, Jefferson, and Monroe.
    For Washington to win, he must beat Jefferson in a one-on-one election, and then defeat Monroe in another one-on-one election.
    Condorcet methods compile ranking ballot data to instantly perform these one-on-one matchups.
    However, it is possible that no candidate is able to beat all other candidates.
    This scenario is called a Condorcet Paradox.
    The many variants of Condorcet methods use various algorithms to resolve Condorcet paradoxes, such as:
    * [Ranked Pairs](https://en.wikipedia.org/wiki/Ranked_pairs)
    * [Smith-minimax](https://electowiki.org/wiki/Smith//Minimax)
    * [Black](https://en.wikipedia.org/wiki/Black%27s_method)
    * [Copeland](https://en.wikipedia.org/wiki/Copeland%27s_method)

  - **[Borda Count](https://en.wikipedia.org/wiki/Borda_count)** -
      Borda cound is a simple ranked method where ranks are converted into points.
      The candidate with the most points wins.

Scored Ballot Methods
---------------------
Scoerd methods rate candidates from a scale. An example scored ballot is shown
below:

![Scored ballot](../static/vote/scoring.png)

Scored methods include:

  - **[Scored voting](https://en.wikipedia.org/wiki/Score_voting)** - Scored voting, or Range voting,
    is a simple system based on rating or grading candidates.
    For example, voters may grade each candidate from a scale of 0 to 5.
    To calculate the winner, the candidate with the greatest sum of scores wins.

  - **[STAR voting (Score then Automatic Runoff)](https://en.wikipedia.org/wiki/STAR_voting)** -
    STAR voting is a variant of score voting with an extra runoff round.
    Score voting has been criticized by some voting theorists to be vulnerable to tactical voting.
    STAR voting was conceived in order to mitigate tactical voting concerns.
    As with score voting, two runoff candidates are chosen based on the sum of candidate scores.
    However, during the runoff phase, the final winner is selected based on the most preferred candidate.
    This runoff serves to encourage voters to express the full range of ballot ratings.

  - **[Smith score](https://electowiki.org/wiki/Smith//Score)** - Smith Score is a
    hybrid combination of scored voting and Condorcet voting systems.
    Smith score chooses the winner using a Condorcet-style selection as well as rated ballots.
    However, if a Condorcet Paradox is encountered, Smith-Score uses scored voting to resolve the paradox.

  - **[Majority judgment](https://en.wikipedia.org/wiki/Majority_judgment)** -
    Majority judgment is another system based on rating or grading candidates.
    However instead of determining the winner from the greatest sum of scores
    (which is equivalent to the average score for each candidate),
    the winner is instead determined from the median score.

Proportional Representation Methods
------------------------------------
Several voting methods have been devised in order to construct
proportionate representation when selecting multiple winners. These methods include:

  - **[Single transferable Vote](https://en.wikipedia.org/wiki/Single_transferable_vote)** - Single Transferable Vote (STV)
    is the multi-winner variant of Instant Runoff Voting. In STV, a candidate is elected when they exceed a quota of votes. 
    If a candidate reaches the quota, surplus votes for that candidate are then transferred to alternatives. STV is used 
    in elections for Australia and Ireland. 
      * [Hare surplus allocation](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Hare) - 
        Ballots are reallocated at random, and exhausted ballots are not reallocated. 
      * [Gregory surplus allocation](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Gregory) - 
        Ballots are reallocated by fractional transfer of value.
  - **[Reweighted Range Voting](https://electowiki.org/wiki/Reweighted_Range_Voting)** - 
    A scored voting system where ballots of voters whose favored candidates win are weighted less and less with each round.  
  - [Sequential Monroe Voting](https://electowiki.org/wiki/Sequential_Monroe_voting) - 
    Another scored proportional voting system. 


Source Code
-----------
Source code for the WebVoter webapp, as well as the voting engine, can be found 
on Github:

 - [votesim Python Package](https://github.com/johnh865/election_sim)
 - [Site source code](https://github.com/johnh865/webvoter)