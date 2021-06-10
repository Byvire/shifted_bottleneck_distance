from collections import Counter
import glob
import logging
import sys
import unittest
import main_algorithm as main
import plane_util as pu
import traceback

class ShiftedBottleneckDistanceTestCase(unittest.TestCase):

    def setUp(self):
        self.log_handler = logging.StreamHandler(sys.stdout)
        self.patched_logger = logging.getLogger("bipartite_matching")
        self.patched_logger.addHandler(self.log_handler)

    def tearDown(self):
        self.patched_logger.removeHandler(self.log_handler)

    def test_sbd_simple_example(self):
        A = Counter([pu.Point(1, 1.2),
                     pu.Point(3, 4)])
        B = Counter([pu.Point(7, 8)])
        self.assert_dist(A, B, 0.1)

    def test_instance_0(self):
        A = [pu.Point(x, y) for x, y in [(0, 2)] * 3 + [(10, 20)]]
        B = [pu.Point(100, 104)]
        self.assert_dist(A, B, 3)

    def test_instance_1(self):
        A = [pu.Point(x, y) for x, y in [(0, 10)] * 3 + [(10, 30)]]
        B = [pu.Point(x, y) for x, y in [(100, 110)] * 3 + [(110, 130)]]
        self.assert_dist(A, B, 0)

    def test_instance_2(self):
        A = [pu.Point(x, y) for x, y in [(0, 10)] * 2 + [(10, 30)]]
        B = [pu.Point(x, y) for x, y in [(100, 110)] * 3 + [(110, 130)]]
        self.assert_dist(A, B, 5)

    def test_instance_3(self):
        """each point occurs only once.  Matching does not involve diagonal."""
        A = [pu.Point(x, y) for x, y in [(1, 4), (4, 7), (3, 8)]]
        B = [pu.Point(x, y) for x, y in [(2, 5), (3, 6), (3, 7)]]
        self.assert_dist(A, B, 1)

    def test_instance_4(self):
        """Same as instance 3, but with a duplicate point mapped to the diagonal."""
        A = [pu.Point(x, y) for x, y in [(1, 4), (1, 4), (4, 7), (3, 8)]]
        B = [pu.Point(x, y) for x, y in [(2, 5), (3, 6), (3, 7)]]
        self.assert_dist(A, B, 1.5)

    def test_when_A_and_B_same(self):
        A = [pu.Point(x, y) for x, y in [(1, 2), (3, 10), (-10.001, 4.8)]]
        B = list(A)
        self.assert_dist(A, B, 0)

    def test_empty_instance(self):
        self.assert_dist([], [], 0)

    def test_floating_point_error(self):
        A = [pu.Point(89.05656796010375, 500.36543481133856),
             pu.Point(475.47639558137354, 943.2982714851478),
             pu.Point(182.629399097048, 608.9632753858887),
             pu.Point(-228.05656095784732, 152.12451765445647),
        ]
        B = [pu.Point(24.211028772142207, 719.2794463444998),
             pu.Point(-8.880085197397246, 778.9696747147142),
             pu.Point(33.85248161012533, 543.4506540489716),
             pu.Point(21.65953167014445, 459.755371873581),
             pu.Point(284.75870352494206, 331.62137217783965),
        ]
        self.assertLess(main.shifted_bottleneck_distance(A, B), 297.336325868691)

    def test_more_floating_point_error(self):
        A = [pu.Point(-251.34757648590244, 588.6044861342364),
             pu.Point(442.9117888626087, 1060.649099507654),
             pu.Point(208.4555953731152, 1172.2315111543112),
             pu.Point(252.90781423572417, 850.8422133407889),
        ]
        B = [pu.Point(-464.67429586980836, 418.5646723227741),
             pu.Point(-329.04480769655964, 350.6552660502859),
             pu.Point(-303.04387560547195, 683.3246912852793),
             pu.Point(190.91717936724763, 809.7956526301617),
             pu.Point(166.57623326229077, 545.7434907850293),
        ]
        self.assertLess(main.shifted_bottleneck_distance(A, B), 419.9760313100694)

    def assert_dist(self, A, B, distance):
        verbose = False
        self.assertAlmostEqual(main.shifted_bottleneck_distance(A, B, analysis=verbose), distance)
        self.assertAlmostEqual(main.shifted_bottleneck_distance(B, A, analysis=verbose), distance)
        self.assertAlmostEqual(main.other_shifted_bottleneck_distance(A, B, analysis=verbose), distance)
        self.assertAlmostEqual(main.other_shifted_bottleneck_distance(B, A, analysis=verbose), distance)

    def test_birth_and_death(self):
        self.assertEqual(main.death(((0, 2), (100, 104)), 5), 105)
        self.assertEqual(main.death(((10, 20), (100, 104)), 5), 89)
        self.assertEqual(main.birth(((10, 20), (100, 104)), 5), 85)
        self.assertEqual(main.birth(((0, 2), (100, 104)), 5), 97)

    def test_sample_instances_do_not_crash(self):
        for A, B, filename in _sample_instances():
            # for filename in glob.glob("sample_instances/*.json"):
            #     with open(filename, "r") as f:
            #         A, B = main.instance_from_file(f)
            try:
                self.assert_dist(A, B, main.shifted_bottleneck_distance(A, B))
            except Exception as e:
                traceback.print_exc()
                raise AssertionError("{} caused crash".format(filename)) from e

def _sample_instances():
    for filename in glob.glob("sample_instances/*.json"):
        with open(filename, "r") as f:
            A, B = main.instance_from_file(f)
            yield (A, B, filename)


if __name__ == "__main__":
    unittest.main()
