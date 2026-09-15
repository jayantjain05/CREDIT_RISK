import unittest

import pandas as pd

from ml.train import normalize_target


class TargetNormalizationTests(unittest.TestCase):
    def test_text_default_labels_are_normalized(self):
        series = pd.Series(["low", "high", "high", "Low"])
        self.assertEqual(normalize_target(series).tolist(), [0, 1, 1, 0])

    def test_binary_numeric_labels_are_normalized(self):
        series = pd.Series([2, 5, 2, 5])
        self.assertEqual(normalize_target(series).tolist(), [0, 1, 0, 1])


if __name__ == "__main__":
    unittest.main()
