#!/usr/bin/pypy3

# See README.md for an explanation

from collections import Counter
from functools import lru_cache
from itertools import product


# Ranges are inclusive of both ends

def range_to_mask(lo, hi):
	return (1 << (hi + 1)) - (1 << lo)


def mask_to_range(mask):
	assert mask
	lo = mask & -mask
	hi = mask + lo
	return lo.bit_length() - 1, hi.bit_length() - 2


def fragment_mask(mask):
	while mask:
		lobit = mask & -mask
		clear_bottom = mask + lobit
		lo = (clear_bottom & -clear_bottom) - 1
		yield mask & lo
		mask &= ~lo


def count_assignments(group_weights):
	rv = 1
	for mask, weight in group_weights.items():
		lo, hi = mask_to_range(mask)
		n = hi + 1 - lo
		assert n > 0
		for _ in range(weight):
			rv *= n
			n -= 1

	return rv


def deintersect_masks(range_masks):
	disjoint_masks = []
	for mask in range_masks:
		next_disjoint_masks = []
		for dm in disjoint_masks:
			intersect = dm & mask
			if intersect:
				next_disjoint_masks.append(intersect)
				mask &= ~intersect
				next_disjoint_masks += list(fragment_mask(dm & ~intersect))
			else:
				next_disjoint_masks.append(dm)

		disjoint_masks = next_disjoint_masks + list(fragment_mask(mask))

	return disjoint_masks


@lru_cache(None)
def bid_threshold(n, bid_seq):
	"""
	Returns the ordinal value of the first card with which the (len(bid_seq)+1)th person would bid 0.
	This is zero-indexed, so 0 corresponds to the highest trump, 1 to the second-highest trump, etc.
	There are 51 cards (because one was removed to indicate the trump suit), so the highest index is 50.
	A returned value of 0 means that the case is impossible if everyone plays correctly.
	"""
	i = len(bid_seq)

	# What ranges do other people's bids indicate?
	thresholds = [bid_threshold(n, bid_seq[:j]) for j in range(i)]
	if 0 in thresholds:
		# A sub-case was impossible, so this is too
		return 0

	ranges = [[(threshold, 50), (0, threshold-1)][bid] for bid, threshold in zip(bid_seq, thresholds)] + [(0, 50)] * (n - i - 1)
	# First player can't have cards above 24, because their card (if not a trump) determines the trick's suit.
	if bid_seq and bid_seq[0] == 0:
		ranges[0] = (thresholds[0], 24)
	range_masks = [range_to_mask(lo, hi) for lo, hi in ranges]

	# If we're not the first bidder, we only bid on a trump.
	upper_limit = 12 if bid_seq else 25

	# Calculate the probability that my card wins.
	# To do this in full generality requires fragmenting the range of cards on the various thresholds.
	disjoint_masks = deintersect_masks(range_masks)
	split_masks = [[dm for dm in disjoint_masks if dm & mask] for mask in range_masks]

	wins_by_my_card = Counter()
	losses_by_my_card = Counter()
	for assignments in product(*split_masks):
		sub_assignments = Counter(assignments)
		min_key = min(sub_assignments)
		lo, hi = mask_to_range(min_key)
		min_key_size = sub_assignments[min_key]

		outright_win = count_assignments(sub_assignments)
		for my_card in range(lo):
			wins_by_my_card[my_card] += outright_win

		loss_assignments = Counter(assignments)
		loss_assignments[min_key] = min_key_size + 1
		# Number of arrangements in which my_card is in [lo, hi] for each value of my_card in [lo, hi]
		total_mine_in_min = count_assignments(loss_assignments) // (hi + 1 - lo)

		for my_card in range(lo, hi):
			# Narrow the range of the cards in the lowest group which lose to my_card
			del sub_assignments[range_to_mask(my_card, hi)]
			sub_assignments[range_to_mask(my_card + 1, hi)] = min_key_size
			inc = count_assignments(sub_assignments)
			wins_by_my_card[my_card] += inc
			losses_by_my_card[my_card] += total_mine_in_min - inc

		for my_card in range(hi, upper_limit):
			# Losses only
			my_mask = 1 << my_card
			loss_assignments = Counter(assignments)
			my_group_width = 1
			for k in assignments:
				if k & my_mask:
					loss_assignments[k] += 1
					my_group_width = mask_to_range(k)[1] + 1 - mask_to_range(k)[0]
					break

			losses_by_my_card[my_card] += count_assignments(loss_assignments) // my_group_width

	for my_card in range(upper_limit):
		# NB <= instead of < catches the impossible situations and returns 0.
		if wins_by_my_card[my_card] <= losses_by_my_card[my_card]:
			return my_card

	return upper_limit


def expected_scores(n):
	sigma_scores = Counter()
	sigma_1 = 0

	for bid_seq in product([0, 1], repeat = n):
		thresholds = [bid_threshold(n, bid_seq[:j]) for j in range(n)]
		if 0 in thresholds:
			continue

		ranges = [[(threshold, 50), (0, threshold-1)][bid] for bid, threshold in zip(bid_seq, thresholds)]

		# Two special cases to handle the dealer not being allowed to make the total bid correct
		if sum(bid_seq) == 1:
			continue
		elif sum(bid_seq[:-1]) + (1 - bid_seq[-1]) == 1:
			ranges[-1] = (0, 50)

		# First player can't have cards above 24, because their card (if not a trump) determines the trick's suit.
		if bid_seq[0] == 0:
			ranges[0] = (thresholds[0], 24)

		range_masks = [range_to_mask(lo, hi) for lo, hi in ranges]
		disjoint_masks = deintersect_masks(range_masks)
		split_masks = [[dm for dm in disjoint_masks if dm & mask] for mask in range_masks]

		wins = [0] * n
		for assignments in product(*split_masks):
			sub_assignments = Counter(assignments)
			min_key = min(assignments)
			wins_per = count_assignments(sub_assignments) // sub_assignments[min_key]
			for i in range(n):
				if assignments[i] == min_key:
					wins[i] += wins_per

		# Scoring for this bid sequence
		seq_weight = sum(wins)
		sigma_1 += seq_weight
		for i, bid in enumerate(bid_seq):
			sigma_scores[i] += wins[i] + 10 * [seq_weight - wins[i], wins[i]][bid]

	return [sigma_scores[i] / sigma_1 for i in range(n)]
