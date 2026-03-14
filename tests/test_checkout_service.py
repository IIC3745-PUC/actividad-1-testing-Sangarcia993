import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	def test_charge_result(self):
		c = ChargeResult(True, "Transaction successful", "reason")
		self.assertTrue(c.ok)
		self.assertEqual(c.charge_id, "Transaction successful")
		self.assertEqual(c.reason, "reason")

	

	def test_checkout_init(self):
		payments = Mock()
		email = Mock()
		fraud = Mock()
		repo = Mock()
		pricing = Mock()
		c = CheckoutService(payments, email, fraud, repo, pricing)
		self.assertEqual(c.payments, payments)
		self.assertEqual(c.email, email)
		self.assertEqual(c.fraud, fraud)
		self.assertEqual(c.repo, repo)
		self.assertEqual(c.pricing, pricing)


	
	def test_checkout_no_user_id(self):
		payments = Mock()
		email = Mock()
		fraud = Mock()
		repo = Mock()
		pricing = Mock()
		c = CheckoutService(payments, email, fraud, repo, pricing)
		result = c.checkout("   ", [], "tok_123", "CL")
		self.assertEqual(result, "INVALID_USER")

	def test_checkout_invalid_cart(self):
		payments = Mock()
		email = Mock()
		fraud = Mock()
		repo = Mock()
		pricing = Mock()
		c = CheckoutService(payments, email, fraud, repo, pricing)
		pricing.total_cents.side_effect = PricingError("invalid cart")
		result = c.checkout("user_1", [CartItem("A", 1000, -1)], "tok_123", "CL")
		self.assertEqual(result, "INVALID_CART:invalid cart")
	
	def test_checkout_fraud(self):
		payments = Mock()
		email = Mock()
		fraud = Mock()
		repo = Mock()
		pricing = Mock()
		c = CheckoutService(payments, email, fraud, repo, pricing)
		fraud.score.return_value = 80
		result = c.checkout("user_1", [CartItem("A", 1000, 2)], "tok_123", "CL")
		self.assertEqual(result, "REJECTED_FRAUD")
	
	def test_checkout_payment_failed(self):
		payments = Mock()
		email = Mock()
		fraud = Mock()
		repo = Mock()
		pricing = Mock()
		c = CheckoutService(payments, email, fraud, repo, pricing)
		fraud.score.return_value = 0
		payments.charge.return_value = ChargeResult(False, "", "Card declined")
		result = c.checkout("user_1", [CartItem("A", 1000, 2)], "tok_123", "CL")
		self.assertEqual(result, "PAYMENT_FAILED:Card declined")


	def test_checkout_success(self):
		payments = Mock()
		email = Mock()
		fraud = Mock()
		repo = Mock(return_value=None)
		pricing = Mock()
		c = CheckoutService(payments, email, fraud, repo, pricing)
		fraud.score.return_value = 0
		
		result = c.checkout("user_1", [CartItem("A", 1000, 2)], "tok_123", "CL")
		self.assertEqual(result, f"OK:{repo.save.call_args.args[0].order_id}")
		