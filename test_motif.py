import random
import unittest

from motif import check_degrees_preserved, count_triads, randomize, zscores


class MotifTests(unittest.TestCase):
    def test_count_triads_counts_connected_triad_once(self):
        counts = count_triads([0, 1, 2], {(0, 1), (1, 2)})

        self.assertEqual(len(counts), 13)
        self.assertEqual(sum(counts), 1)

    def test_count_triads_ignores_disconnected_pairs(self):
        counts = count_triads([0, 1, 2, 3], {(0, 1), (2, 3)})

        self.assertEqual(sum(counts), 0)

    def test_randomize_preserves_degrees_and_simple_edges(self):
        edges = {(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (2, 0)}

        randomized = randomize(edges, 100, random.Random(42))

        check_degrees_preserved(edges, randomized)
        self.assertEqual(len(randomized), len(set(randomized)))
        self.assertTrue(all(u != v for u, v in randomized))

    def test_zscores_returns_zero_for_constant_random_counts(self):
        observed = [1] * 13
        random_counts = [[2] * 13, [2] * 13]

        self.assertEqual(zscores(observed, random_counts), [0.0] * 13)


if __name__ == "__main__":
    unittest.main()
