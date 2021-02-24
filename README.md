Analysis of one-card Oh Hell!
=============================

There are undoubtedly many variants of the card game Oh Hell!, so in case of discrepancy this analysis is based on the
version implemented at [boardgamearena.com](https://en.boardgamearena.com/gamepanel?game=ohhell).

When each player has two or more cards, the order in which they play them depends on various factors which make
analysis difficult. But when each player has only one card they have one choice each (except, in most cases, the
dealer), and it's possible to perform a full analysis subject to certain assumptions.

In particular, I assume that players do not bluff and aim to maximise their own expected score. Also, since this study
is motivated by practical application, I will assume a standard deck of 52 cards in 4 suits and `3 <= n <= 7` players.
And as a question of personal and playing group preference, I will assume "positive" scoring.

If the probability that player `i` wins the trick is `p_i`, their expected score if bidding 0 is
`10 (1 - p_i) + p_i = 10 - 9 p_i` and their expected score if bidding 1 is `11 p_i` so they should bid 1 if
`11 p_i > 10 - 9 p_i` i.e. `p_i > 1/2` which is nicely straightforward.

The first player has to bid with no information, and their card determines the suit for the trick. The cases where they
do or don't have a trump are essentially the same, because either way there is a known number of cards (from 0 if they
have the ace of trumps, to 24 if they have the 2 of a side suit) which beat them, so we parameterise on that number,
`k`. Then the probability of winning is the probability that none of the other `n-1` players has one of those `k` cards
from the 50 remaining: i.e. `p_1 = (50 - k)*...*(50 - k - n + 2) / 50*...*(50 - n + 2)`.

                                                                         holding
     Probability of winning                                               lowest
                                                                          trump    a     k     q     j
      k   0     1     2     3     4     5     6     7     8     9     10    11    12    13    14    15
     n=3  1  0.96  0.92  0.88  0.84  0.81  0.77  0.74  0.70  0.67  0.637  0.60  0.57  0.54  0.51  0.49
     n=4  1  0.94  0.88  0.83  0.77  0.72  0.68  0.63  0.59  0.54  0.504  0.47
     n=5  1  0.92  0.84  0.77  0.71  0.65  0.59  0.54  0.49
     n=6  1  0.90  0.81  0.72  0.65  0.58  0.51  0.45
     n=7  1  0.88  0.77  0.68  0.59  0.51  0.44

So with `n = 3` the first player should bid 1 holding a queen in a side suit; otherwise they should bid 1 only with
a trump. Observe that the case `n = 4` holding the 2 of trumps is an example of a counterintuitive result: there are 11
cards out of 50 which can beat it, so a 0th order approximation would be that there's an expected 0.66 cards in play
which can beat it, but the odds that it wins are less than 50:50. With `n = 4` the first player should bid 1 on the
second-lowest trump or better; with `n` in `{5, 6, 7}` on the `n`th lowest trump or better.

For the other players, we can calculate blind and informed assessed values. A card in a side suit, even the ace, can
only win if the first player has the same suit (blind probability 12/50, informed probability no higher), so we always
bid 0. Holding a trump, for the blind values the same thresholds as for the first player should apply. For the
informed values, we need to consider all possible sequences of bids. Python code for this analysis is supplied in a
[separate file](https://github.com/pjt33/oh_hell_analysis/blob/master/one_card_analysis.py).


Tables of results
-----------------

In each of these tables the symbol indicates the lowest trump on which to bid 1, assuming that the revealed card is
the ace. Adjust up by one if the revealed card is lower than or equal to the indicated card. The lower-case `q` in the
first table indicates the only correct bid of 1 when holding a non-trump: queen of side suit or better.

When previous bids total 0: dealer bids 0 like it or not (which they don't if they have any trump!)

    Previous bid sequence         n
                              3 4 5 6 7
    -----------------------------------
    ()                        q 3 6 7 8
    (0,)                      2 2 4 6 7
    (0, 0)                    * 2 2 5 6
    (0, 0, 0)                 . * 2 3 5
    (0, 0, 0, 0)              . . * 2 4
    (0, 0, 0, 0, 0)           . . . * 2


When previous bids total 1: dealer bids 1 like it or not (which they don't most of the time).

    Previous bid sequence         n
                              3 4 5 6 7
    -----------------------------------
    (1,)                      7 9 J J Q
    
    (0, 1)                    * 9 T J J
    (1, 0)                    * 9 J J Q
    
    (0, 0, 1)                 . * 9 T J
    (0, 1, 0)                 . * 9 J J
    (1, 0, 0)                 . * T J J
    
    (0, 0, 0, 1)              . . * 9 T
    (0, 0, 1, 0)              . . * T J
    (0, 1, 0, 0)              . . * T J
    (1, 0, 0, 0)              . . * J J
    
    (0, 0, 0, 0, 1)           . . . * T
    (0, 0, 0, 1, 0)           . . . * T
    (0, 0, 1, 0, 0)           . . . * T
    (0, 1, 0, 0, 0)           . . . * J
    (1, 0, 0, 0, 0)           . . . * J


When previous bids total 2: dealer has free bid. Cases where independently of `n` you only bid 1 with the top trump
have been elided as unnecessary: if you have the top trump, you don't need to consult a table to know whether to bid
it.

    Previous bid sequence         n
                              3 4 5 6 7
    -----------------------------------
    (1, 1)                    J Q K K K
    
    (0, 1, 1)                 . Q Q K K
    (1, 0, 1)                 . Q K K K
    (1, 1, 0)                 . Q K K K
    
    (0, 0, 1, 1)              . . Q Q K
    (0, 1, 0, 1)              . . Q K K
    (0, 1, 1, 0)              . . Q K K
    (1, 0, 0, 1)              . . Q K K
    
    (0, 0, 0, 1, 1)           . . . Q Q
    (0, 0, 1, 0, 1)           . . . Q K
    (0, 0, 1, 1, 0)           . . . Q K
    (0, 1, 0, 0, 1)           . . . Q K
    
    (0, 0, 0, 0, 1, 1)        . . . . Q
    (0, 0, 0, 1, 0, 1)        . . . . Q
    (0, 0, 0, 1, 1, 0)        . . . . Q
    (0, 0, 1, 0, 0, 1)        . . . . Q

    
When previous bids total 3 or more: bid 1 only with the top trump. Many of these cases are impossible anyway if
everyone follows this guide.
