import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):
	def test_subtotal_cents(self):
		p = PricingService()
		items = [
			CartItem("A", 1000, 2),
			CartItem("B", 500, 3),
		]
		self.assertEqual(p.subtotal_cents(items), 3500)
	
	def test_subtotal_cents_raise_inv_qty(self):
		p = PricingService()
		items = [
			CartItem("A", 1000, 0),
		]
		self.assertRaises(PricingError, p.subtotal_cents, items)

	def test_subtotal_cents_raise_unit_price(self):
		p = PricingService()
		items = [
			CartItem("A", -1, 2),
		]
		self.assertRaises(PricingError, p.subtotal_cents, items)

	

	def test_apply_coupon_none(self):
		p = PricingService()
		self.assertEqual(p.apply_coupon(10000, None), 10000)
		self.assertEqual(p.apply_coupon(10000, ""), 10000)
		self.assertEqual(p.apply_coupon(10000, "   "), 10000)
	
	def test_apply_coupon_save10(self):
		p = PricingService()
		self.assertEqual(p.apply_coupon(10000, "  SAVE10"), 9000)
		self.assertEqual(p.apply_coupon(9999, "SaVE10"), 9000)
	
	def test_apply_coupon_clp2000(self):
		p = PricingService()
		self.assertEqual(p.apply_coupon(10000, "CLP2000"), 8000)
		self.assertEqual(p.apply_coupon(1500, "CLP2000"), 0)
	
	def test_apply_coupon_raise(self):
		p = PricingService()
		self.assertRaises(PricingError, p.apply_coupon, 10000, "INVALIDO")


	
	def test_tax_cents(self):
		p = PricingService()
		self.assertEqual(p.tax_cents(10000, "CL"), 1900)
		self.assertEqual(p.tax_cents(10000, "EU"), 2100)
		self.assertEqual(p.tax_cents(10000, "US"), 0)
	
	def test_tax_cents_raise(self):
		p = PricingService()
		self.assertRaises(PricingError, p.tax_cents, 10000, "XX")

	

	def test_shipping_cents(self):
		p = PricingService()
		self.assertEqual(p.shipping_cents(10000, "CL"), 2500)
		self.assertEqual(p.shipping_cents(20000, "CL"), 0)
		self.assertEqual(p.shipping_cents(10000, "US"), 5000)
		self.assertEqual(p.shipping_cents(10000, "EU"), 5000)
	
	def test_shipping_cents_raise(self):
		p = PricingService()
		self.assertRaises(PricingError, p.shipping_cents, 10000, "XX")

	

	def test_total_cents(self):
		p = PricingService()
		items = [
			CartItem("A", 1000, 2),
			CartItem("B", 500, 3),
		]
		self.assertEqual(p.total_cents(items, None, "CL"), 6665)
