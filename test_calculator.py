# test_calculator.py

import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):

    def setUp(self):
        """Set up a Calculator instance before each test"""
        self.calc = Calculator()

    def test_add(self):
        """Test addition operation"""
        self.assertEqual(self.calc.add(5, 3), 8)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(-2, -3), -5)

    def test_subtract(self):
        """Test subtraction operation"""
        self.assertEqual(self.calc.subtract(10, 5), 5)
        self.assertEqual(self.calc.subtract(0, 3), -3)

    def test_multiply(self):
        """Test multiplication operation"""
        self.assertEqual(self.calc.multiply(4, 5), 20)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
        self.assertEqual(self.calc.multiply(0, 5), 0)

    def test_divide(self):
        """Test division operation"""
        self.assertEqual(self.calc.divide(10, 2), 5)
        self.assertAlmostEqual(self.calc.divide(7, 3), 2.3333, places=4)

        # Test division by zero
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)


if __name__ == '__main__':
    unittest.main()
