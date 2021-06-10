import unittest
from collections import Counter

import bipartite_matching as bpm
import plane_util as pu

class MatchingTestCase(unittest.TestCase):

    def test_basics(self):
        m = bpm.Matching()
        m.augment_path("a", "x", mult=7)
        self.assertEqual(len(m), 7)  # should have 7 edges
        m.augment_path("b", "y", mult=3)
        self.assertEqual(len(m), 10)
        m.augment_path("c", "x", "a", "z", mult=4)
        self.assertEqual(len(m), 14)
        self.assertEqual(m.degree("a", in_A=True), 7)
        self.assertEqual(m.degree("x", in_A=False), 7)
        self.assertEqual(m.degree("y", in_A=False), 3)

        m.augment_path("c", "y", "b", "z", mult=3)
        self.assertEqual(len(m), 17)
        self.assertFalse(m.has_edge("b", "y"))
        self.assertEqual(m.degree("b", in_A=True), 3)
        self.assertEqual(m.remove_edge("a", "x"), 3)
        self.assertEqual(len(m), 14)
        self.assertEqual(m.degree("a", in_A=True), 4)
        self.assertFalse(m.has_edge("a", "x"))


class GeometricBipartiteMatchingTestCase(unittest.TestCase):

    def test_maximizing_matching(self):
        self.maxDiff = None
        A = [pu.Point(0, 2), pu.Point(2, 5), pu.Point(2, 5)]
        B = [pu.Point(1, 3), pu.Point(3, 6), pu.Point(3, 6)]
        gm = bpm.GeometricBipartiteMatching(A, B)
        self.assert_sanity(gm)
        self.assertFalse(gm.diagonal_perfect())
        gm.maximize_matching(shift=100, radius=1.5)
        self.assert_edges(gm, [(A[0], pu.Point(1, 1)),
                               (pu.Point(2, 2), B[0])])
        self.assert_sanity(gm)
        self.assertFalse(gm.diagonal_perfect())
        gm.maximize_matching(shift=100, radius=1.6)
        self.assert_sanity(gm)
        expected_edges = [(A[0], pu.Point(1, 1)),
                          (pu.Point(2, 2), B[0]),
                          (A[1], pu.Point(3.5, 3.5)),
                          (A[2], pu.Point(3.5, 3.5)),
                          (pu.Point(4.5, 4.5), B[1]),
                          (pu.Point(4.5, 4.5), B[2]),
        ]
        self.assert_edges(gm, expected_edges)
        self.assertTrue(gm.diagonal_perfect())
        self.assertEqual(gm.value(), 1.5)
        gm.remove_all((pu.Point(4.5, 4.5), B[2]))
        self.assert_sanity(gm)
        self.assert_edges(gm, expected_edges[:-2])  # both copies should be gone
        for edge in set(expected_edges):
            gm.remove_all(edge)
            self.assert_sanity(gm)
        self.assert_edges(gm, [])
        # Now let's go for the gold
        gm.maximize_matching(shift=1, radius=0.01)
        self.assert_edges(gm, zip(A, B))
        self.assert_sanity(gm)
        self.assertTrue(gm.diagonal_perfect())
        self.assertEqual(gm.value(), 0)

    def _hanging_fp_instance(self):
        A = [(-432.94192024932653, 530.4790466084148),
             (-74.80546818492695, 626.5615783097762),
             (-41.80335706574778, 471.59244059361),
             (83.502317202234, 701.7752831612759)]
        B = [(-88.19548216309259, 712.4423352854286),
             (272.41092384415913, 767.7859742332469),
             (342.50568447861497, 556.6237276823114),
             (-356.433692180247, -347.40233149573567),
             (-112.29496070525525, 244.21351549241152)]
        return A, B

    # @unittest.skip("no reason")
    def test_floating_point_error_case(self):
        # at time of writing, this sequence of operations causes an infinite loop
        A, B = self._hanging_fp_instance()
        gm = bpm.GeometricBipartiteMatching(A, B)
        radius = pu.dist_from_diag(A[0])
        # radius = 481.7104834288707
        gm.maximize_matching(radius=radius, shift=-858.9936556773607, closed=False)
        self.assertFalse(gm.diagonal_perfect())
        gm.maximize_matching(radius=radius, shift=-779.8397629837802, closed=False)
        self.assertFalse(gm.diagonal_perfect())
        gm.maximize_matching(radius=radius, shift=-720.4232343802753, closed=False)
        self.assertFalse(gm.diagonal_perfect())
        gm.maximize_matching(radius=radius, shift=-622.4874462822504, closed=False)
        self.assertFalse(gm.diagonal_perfect())
        gm.remove_all((A[3], B[3]))  # edge died a natural death
        self.assertFalse(gm.diagonal_perfect())
        gm.maximize_matching(radius=radius, shift=-535.7010315087884, closed=False)
        gm.maximize_matching(radius=radius, shift=-505.72670116292005, closed=False)
        gm.remove_all((A[1], B[3]))
        self.assertFalse(gm.has_edge(A[0], gm.B_diag))
        gm.maximize_matching(radius=radius, shift=-438.12284333225455, closed=False)
        self.assertFalse(gm.has_edge(A[0], gm.B_diag))        
        self.assertFalse(gm.diagonal_perfect())  # no edges involve A[0] by this time

    def test_floating_point_error_more_simply(self):
        A, B = self._hanging_fp_instance()
        gm = bpm.GeometricBipartiteMatching(A, B)
        gm.maximize_matching(radius=481.7104834288707, shift=-438.12284333225455, closed=False)
        self.assertFalse(gm.diagonal_perfect())

    def assert_edges(self, matching, edges):
        def fix_diagonals(edge):
            if edge[0][0] == edge[0][1]:
                return (matching.A_diag, edge[1])
            elif edge[1][0] == edge[1][1]:
                return (edge[0], matching.B_diag)
            else:
                return edge
        backup, self.longMessage = self.longMessage, True
        self.assertEqual(Counter((edge[0], edge[1]) for edge in matching.edges(repeats=True)
                                 if edge[0] != matching.A_diag or edge[1] != matching.B_diag),
                         Counter(fix_diagonals(e) for e in edges),
                         msg="\nexpected: {}\nactual: {}".format(
                             Counter(edges),
                             Counter(matching.edges(repeats=True))))
        self.longMessage = backup

    def assert_sanity(self, matching):
        assert_sanity(self, matching)

def assert_sanity(self, matching):
    for a in matching.A:
        self.assertEqual(matching.A[a] - matching.matching.degree(a, in_A=True),
                         matching.A_exposed[a])
    for b in matching.B:
        self.assertEqual(matching.B[b] - matching.matching.degree(b, in_A=False),
                         matching.B_exposed[b])

class BipartiteFunctionalTestCase(unittest.TestCase):

    def test_edge_to_vee(self):
        a = pu.Point(4, 8)
        b = pu.Point(10, 12)
        (shift, radius) = bpm.edge_to_vee((a, b))
        a_shifted = pu.Point(a[0] + shift, a[1] + shift)
        self.assertEqual(pu.infty_metric(a_shifted, b), radius)
        self.assertEqual(a_shifted, pu.Point(9, 13))
        self.assertEqual(radius, 1)
        self.assertEqual((-shift, radius),
                         bpm.edge_to_vee((b, a)))

        self.assertEqual((3, 0),
                         bpm.edge_to_vee(((1, 2), (4, 5))))

    def test_intersect_diagonal_lines(self):
        self.assertEqual(pu.Point(0, 0),
                          bpm.intersect_diagonal_lines((-1, 1), (1, 1)))
        self.assertEqual(pu.Point(10, 0),
                          bpm.intersect_diagonal_lines((5, 5), (5, -5)))
        self.assertEqual(pu.Point(9, 13),
                         bpm.intersect_diagonal_lines((10, 12), (4, 8)))
        self.assertEqual(pu.Point(4, 4),
                         bpm.intersect_diagonal_lines((4, 4), (4, 4)))

        # self.assertEqual(pu.Point(10, 0),
        #                   bpm.intersect_diagonal_lines((5, 5), (5, -5)))
if __name__ == "__main__":
    unittest.main()
