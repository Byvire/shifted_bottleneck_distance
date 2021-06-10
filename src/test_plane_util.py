#!/usr/bin/env python3
import unittest
import plane_util as pu

class PlaneUtilFunctionalTestCase(unittest.TestCase):

    def test_dist_to_diag(self):
        self.assertEqual(pu.dist_from_diag(pu.Point(3, 3)),
                         0)
        self.assertEqual(pu.dist_from_diag(pu.Point(3, 4)),
                         0.5)

    def test_closest_diag_point(self):
        self.assertEqual(pu.closest_diag_point(pu.Point(3, 4)),
                         pu.Point(3.5, 3.5))

    def test_sort_convex_points_ccw(self):
        square = [pu.Point(0, 0), pu.Point(0, 1), pu.Point(1, 0), pu.Point(1, 1)]
        sorted_square = pu.sort_convex_vertices_ccw(*square)
        origin_index = sorted_square.index(pu.Point(0, 0))
        sorted_square = sorted_square[origin_index:] + sorted_square[:origin_index]
        self.assertEqual(sorted_square,
                         [pu.Point(0, 0),
                          pu.Point(1, 0),
                          pu.Point(1, 1),
                          pu.Point(0, 1)])

    def test_ccw(self):
        self.assertEqual(pu.ccw(pu.Point(0, 0), pu.Point(1, 0), pu.Point(2, 0)),
                         0)
        self.assertEqual(pu.ccw(pu.Point(1, 0), pu.Point(0, 1), pu.Point(-2, -1)),
                         1)
        self.assertEqual(pu.ccw(pu.Point(0, 1), pu.Point(1, 0), pu.Point(-2, -1)),
                         -1)

    def test_quick_select(self):
        pu.random.seed(0, version=2)
        sample_list = [10, 1, 9, 4, 3, 8, 2, 7, 6, 2, 2]  # 1 2 2 2 3 4 6 7 8 9 10
        self.assertEqual(pu.quick_select(sample_list, 5),
                         4)  # fix these
        self.assertEqual(pu.quick_select(sample_list, 6),
                         6)
        self.assertEqual(pu.quick_select(sample_list, 3),
                         2)
        self.assertEqual(pu.quick_select(sample_list, 1, key=lambda x: -x),
                         9)

class ConvexShapeTestCase(unittest.TestCase):

    def test_point_finding(self):
        my_shape = pu.convex_shape(pu.Point(-1, 0),
                                   pu.Point(0, 1),
                                   pu.Point(1, 1),
                                   pu.Point(2, -1),
                                   pu.Point(-1, -1))
        self.assertEqual(my_shape.contains(pu.Point(0, 0)),
                         1)
        self.assertEqual(my_shape.contains(pu.Point(1, 2)),
                         -1)
        self.assertEqual(my_shape.contains(pu.Point(-0.5, 0.5)),
                         0)


# class KDTreeTestCase(unittest.TestCase):

#     kdtree_cls = pu.SimpleKDTree
#     def setUp(self):
#         pu.random.seed(0, version=2)
#         self.example = self.kdtree_cls(*(pu.Point(x, y) for (x, y) in (
#             (0, 0), (0, 1), (1, 0), (1, 1), (3, 5), (-10, 4))))

#         self.colinear_example = self.kdtree_cls(
#             *(pu.Point(3.5, y) for y in (-5, -4.7, 3, 10, 11)))

#         self.large_example = [(x, y) for x in range(-40, 40) for y in range(-40, 40)]

#     def assert_equal_unordered(self, list1, list2):
#         self.assertEqual(sorted(list1, key=hash),
#                          sorted(list2, key=hash))

#     def assert_points_result(self, points, tuples):
#         self.assert_equal_unordered(points, [pu.Point(*tup) for tup in tuples])

#     def test_range_search_correctness(self):
#         self.assert_points_result(
#             self.example.neighbor(pu.Point(0, 0.5), radius=1, closed=False), # search_ranges((-0.5, 0.5), (-0.5, 1.5)),
#             [(0, 0), (0, 1)])
#         # edge cases.  Rectangle is closed.
#         self.assert_points_result(
#             self.example.search_ranges((0, 1), (0, 1)),
#             [(0, 0), (0, 1), (1, 0), (1, 1)])

#         # self.assertEqual(len(self.example.search_ranges((0, 1), (0, 1))),
#         #                  4)

#         self.assert_points_result(
#             self.example.search_ranges((-10, 0.5), (0.5, 10)),
#             [(0, 1), (-10, 4)])

#     # def test_range_search_more(self):
#     #     self.large_example.search_ranges((

#     def test_empty_tree(self):
#         tree = self.kdtree_cls()
#         self.assertEqual(tree.neighbor(pu.Point(1, 2)),
#                          None)

#     def test_range_search_more_dimensions(self):
#         cube_points = [pu.Point(x, y, z) for x in [-1, 1] for y in [-1, 1] for z in [-1, 1]]
#         cube = self.kdtree_cls(*cube_points)
#         self.assert_points_result(
#             cube.search_ranges((-1, 1), (-1, 1), (-2, 0)),
#             [(x, y, -1) for x in (-1, 1) for y in (-1, 1)])


class EfratTestCaseMixin:
    efrat_cls = None

    def whatever_points(self):
        return [pu.Point(x, y) for (x, y) in
                [(-1.5, -0.5), (-1, 0), (-1, 1), (-1, 2),
                 (0.3, 0.4), (0.7, 1.2), (0.75, 1.5), (0.8, -0.9)]]

    def test_open_without_multiplicity(self):
        points = self.whatever_points()
        efrat = self.efrat_cls(*points, radius=1, closed=False)
        self.assertEqual(efrat.neighbor(pu.Point(0, -1)),
                         pu.Point(0.8, -0.9))
        efrat.delete(pu.Point(0.8, -0.9))
        self.assertEqual(efrat.neighbor(pu.Point(0, -1)), None)

        self.assertIn(efrat.neighbor(pu.Point(0, 2)), points[5:7])
        efrat.delete(points[5])
        self.assertEqual(efrat.neighbor(pu.Point(0, 2)), points[6])
        efrat.delete(points[6])
        self.assertEqual(efrat.neighbor(pu.Point(0, 2)), None)

    def test_closed_without_multiplicity(self):
        points = self.whatever_points()
        efrat = self.efrat_cls(*points, radius=1, closed=True)
        count = 0
        while efrat.neighbor(pu.Point(0, 1)) is not None:
            count += 1
            efrat.delete(efrat.neighbor(pu.Point(0, 1)))
        self.assertEqual(count, 6)

        with self.assertRaises(KeyError):
            # bogus point
            efrat.delete(pu.Point(1, 2))
        with self.assertRaises(KeyError):
            # deleted previously
            efrat.delete(points[3])

    def test_closed_with_multiplicity(self):
        points = self.whatever_points()
        efrat = self.efrat_cls(*(points * 4), radius=1, closed=True)
        self.assertEqual(efrat.count(points[0]), 4)
        count = 0
        while efrat.neighbor(pu.Point(0, 1)) is not None:
            count += 1
            efrat.delete(efrat.neighbor(pu.Point(0, 1)), mult=2)
        self.assertEqual(count, 12)
        with self.assertRaises(KeyError):
            efrat.delete(points[0], mult=8)
        # recover from bad deletion queries by not processing them
        self.assertEqual(efrat.neighbor(pu.Point(-2.5, 0)), points[0])
        self.assertEqual(efrat.count(points[0]), 4)
        self.assertEqual(efrat.count(points[4]), 0)

class MultiEfratKDTreeTestCase(unittest.TestCase, EfratTestCaseMixin):
    efrat_cls = pu.MultiEfratKDTree

class EfratTreeWithDiagonalTestCase(unittest.TestCase, EfratTestCaseMixin):
    efrat_cls = pu.EfratTreeWithDiagonal

    def test_open_with_diagonal(self):
        points = [pu.Point(1, 3)]
        diag_key = "my diag token"
        other_diag = "other diag token"
        efrat = self.efrat_cls(*(points*5 + [diag_key] * 6), radius=2,
                               diag_key=diag_key, other_diag=other_diag,
                               closed=False)
        self.assertEqual(efrat.count(diag_key), 6)
        self.assertEqual(efrat.neighbor(pu.Point(0, 4)),
                         points[0])
        self.assertEqual(efrat.neighbor(pu.Point(10, 11)), diag_key)
        self.assertIn(efrat.neighbor(other_diag), [diag_key, points[0]])
        count = 0
        while efrat.neighbor(pu.Point(10, 11)) is not None:
            count += 2
            efrat.delete(efrat.neighbor(pu.Point(10, 11)), mult=2)
            self.assertLess(count, 100, "infinite loop")
        self.assertEqual(count, 6)
        self.assertEqual(efrat.count(diag_key), 0)
        self.assertEqual(efrat.neighbor(other_diag), points[0])
        count = 0
        while efrat.neighbor(other_diag) is not None:
            count += 1
            efrat.delete(efrat.neighbor(other_diag))
            self.assertLess(count, 40, "infinite loop again")
        self.assertEqual(count, 5)

    def test_closed_with_diagonal(self):
        points = [pu.Point(1, 3), pu.Point(10, 14), "diag"]
        other_diag = "other diag"
        efrat = self.efrat_cls(*(points*5), points[2], radius=2, diag_key=points[2],
                               other_diag=other_diag, closed=True)
        self.assertIn(efrat.neighbor(pu.Point(0, 4)),
                      (points[0], points[2]))
        count = 0
        while efrat.neighbor(pu.Point(0, 4)) is not None:
            count += 1
            efrat.delete(efrat.neighbor(pu.Point(0, 4)))
            self.assertLess(count, 40, "infinite loop again")
        self.assertEqual(count, 11)

        self.assertEqual(points[1], efrat.neighbor(other_diag))
        count = 0
        while efrat.neighbor(other_diag) is not None:
            count += 1
            efrat.delete(efrat.neighbor(other_diag))
            self.assertLess(count, 40, "infinite loop again")
        self.assertEqual(count, 5)

    def test_deleting_all(self):
        points = [pu.Point(1, 3), "diag"]
        efrat = self.efrat_cls(*(points * 7), radius=0.4, diag_key=points[1],
                               other_diag="other", closed=True)
        self.assertEqual(efrat.neighbor("other"), points[1])
        efrat.delete(points[1], mult=-1)
        self.assertEqual(efrat.neighbor("other"), None)

    def test_initializing_with_dictionary(self):
        points = [pu.Point(1, 3), "diag"]
        efrat = self.efrat_cls({point: 7 for point in points},
                               radius=0.4, diag_key=points[1],
                               other_diag="other", closed=True)
        self.assertEqual(efrat.neighbor("other"), points[1])

    def test_empty_except_diagonal(self):
        efrat = self.efrat_cls("diag", "diag", "diag",
                               diag_key="diag", other_diag="other")
        self.assertEqual(efrat.count("diag"), 3)
        self.assertEqual(efrat.neighbor("other"), "diag")



if __name__ == "__main__":
    unittest.main()
