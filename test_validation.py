import unittest
import math
from src.validation import OrderValidator, ValidationError

class TestValidation(unittest.TestCase):

    def test_quantity_nan_inf(self):
        with self.assertRaisesRegex(ValidationError, "Quantity must be a finite number"):
            OrderValidator.validate_quantity(float('nan'))

        with self.assertRaisesRegex(ValidationError, "Quantity must be a finite number"):
            OrderValidator.validate_quantity(float('inf'))

        with self.assertRaisesRegex(ValidationError, "Quantity must be a finite number"):
            OrderValidator.validate_quantity(float('-inf'))

    def test_price_nan_inf(self):
        with self.assertRaisesRegex(ValidationError, "Price must be a finite number"):
            OrderValidator.validate_price(float('nan'))

        with self.assertRaisesRegex(ValidationError, "Price must be a finite number"):
            OrderValidator.validate_price(float('inf'))

        with self.assertRaisesRegex(ValidationError, "Price must be a finite number"):
            OrderValidator.validate_price(float('-inf'))

    def test_stop_price_nan_inf(self):
        with self.assertRaisesRegex(ValidationError, "Stop price and entry price must be finite numbers"):
            OrderValidator.validate_stop_price(float('nan'), 100, 'BUY')

        with self.assertRaisesRegex(ValidationError, "Stop price and entry price must be finite numbers"):
            OrderValidator.validate_stop_price(100, float('nan'), 'BUY')

        with self.assertRaisesRegex(ValidationError, "Stop price and entry price must be finite numbers"):
            OrderValidator.validate_stop_price(float('inf'), 100, 'BUY')

        with self.assertRaisesRegex(ValidationError, "Stop price and entry price must be finite numbers"):
            OrderValidator.validate_stop_price(100, float('-inf'), 'BUY')

    def test_percentage_nan_inf(self):
        with self.assertRaisesRegex(ValidationError, "Percentage must be a finite number"):
            OrderValidator.validate_percentage(float('nan'))

        with self.assertRaisesRegex(ValidationError, "Percentage must be a finite number"):
            OrderValidator.validate_percentage(float('inf'))

        with self.assertRaisesRegex(ValidationError, "Percentage must be a finite number"):
            OrderValidator.validate_percentage(float('-inf'))

if __name__ == '__main__':
    unittest.main()
