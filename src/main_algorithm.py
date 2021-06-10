"""
Here the algorithm from the paper is implemented, with lots of ugly debugging
statements.

If I remember correctly, `other_shifted_bottleneck_distance` is the version
that made it into the paper.
"""

from collections import namedtuple

from bipartite_matching import GeometricBipartiteMatching
import plane_util as pu
import event_queue
from event_queue import Edge, birth, death, Stack

import json

epsilon = 0.00000000001

# What if we stop computing the value of the matching and just start ticking the radius down to where the next edge will die?
# 2021 addendum: What if I just leave notes to myself in random places and never clean them up?
# That was a good idea and made it into the paper though.

def default_fudge(r):
    return r * (1 - epsilon)

def upper_bound_on_radius(A, B):
    return max(pu.dist_from_diag(x) for x in A + B)

def shifted_bottleneck_distance(A, B, fudge=default_fudge, analysis=False):
    """Compute the shifted bottleneck distance between two diagrams, A and B (multisets).

    2021 note: this looks like an earlier version of the algorithm. Use the other version,
    defined below.
    """
    A = pu.SaneCounter(A)
    B = pu.SaneCounter(B)
    if not A and not B:
        return 0
    radius = fudge(upper_bound_on_radius(A, B))
    events = event_queue.EventQueue(A, B)
    matching = GeometricBipartiteMatching(A, B)
    # these counters are for performance monitoring only - they don't affect the logic
    ctr, R_ctr, L_ctr, fail_ctr, win_ctr = 0, 0, 0, 0, 0
    while events and radius > epsilon:
        ctr += 1
        event = events.next_event(radius)
        if isinstance(event, event_queue.ExitEvent):
            R_ctr += 1
            matching.remove_all(event.edge)
        else:
            L_ctr += 1
            if birth(event.edge, radius) >= death(event.edge, radius):
                win_ctr += 1
                continue  # relies on ties being broken with the highest-radius edge
            # assert not matching.diagonal_perfect()
            if matching.diagonal_perfect():
                fail_ctr += 1
                radius = fudge(max(
                    events.next_diagonal_height(),
                    radius - (events.next_exit_shift(radius)
                              - birth(event.edge, radius)) / 2))
                events.push(event)
                continue
            matching.maximize_matching(
                shift=event.shift_to_check,
                radius=radius)
            if matching.diagonal_perfect():
                radius = fudge(matching.value())
                events.push(event)
    if analysis:
        print(len(A) + len(B), "total", ctr, "R", R_ctr, "L", L_ctr, "fail", fail_ctr, "win", win_ctr)
    return radius

def other_shifted_bottleneck_distance(A, B, fudge=default_fudge, analysis=False):
    """Compute the shifted bottleneck distance between two diagrams, A and B (multisets)"""
    A = pu.SaneCounter(A)
    B = pu.SaneCounter(B)
    if not A and not B:
        return 0
    radius = fudge(upper_bound_on_radius(A, B))
    events = event_queue.EventQueue(A, B)
    matching = GeometricBipartiteMatching(A, B)
    # these counters are for performance monitoring only - they don't affect the logic
    ctr, R_ctr, L_ctr, fail_ctr, win_ctr = 0, 0, 0, 0, 0
    while events and radius > epsilon:
        ctr += 1
        event = events.next_event(radius)
        if isinstance(event, event_queue.ExitEvent):
            R_ctr += 1
            matching.remove_all(event.edge)
        else:
            L_ctr += 1
            if birth(event.edge, radius) >= death(event.edge, radius):
                win_ctr += 1
                continue  # relies on ties being broken with the highest-radius edge
            # assert not matching.diagonal_perfect()
            if matching.diagonal_perfect():
                fail_ctr += 1
                radius = fudge(max(
                    events.next_diagonal_height(),
                    radius - (events.next_exit_shift(radius)
                              - birth(event.edge, radius)) / 2))
                events.push(event)
                continue
            matching.maximize_matching(
                shift=event.shift_to_check,
                radius=radius)
            if matching.diagonal_perfect():
                # radius = fudge(matching.value())
                events.push(event)
    if analysis:
        print("other:", len(A) + len(B), "total", ctr, "R", R_ctr, "L", L_ctr, "fail", fail_ctr, "win", win_ctr)
    return radius


def instance_from_file(file_):

    instance = json.load(file_)
    A = [pu.Point(*pt) for pt in instance['A']]
    B = [pu.Point(*pt) for pt in instance['B']]
    return A, B

if __name__ == "__main__":
    import sys
    A, B = instance_from_file(sys.stdin)
    print(shifted_bottleneck_distance(A, B))
