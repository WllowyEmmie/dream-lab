import unittest

from store.refunds import Payment


class HiddenTest(unittest.TestCase):
    def test_card_before_gift_card_still_works(self):
        payment = Payment([("gift_card", 3000), ("card", 5000)])
        self.assertEqual(payment.refund(4000), {"card": 4000})

    def test_order_is_card_cash_gift_card(self):
        payment = Payment([("gift_card", 3000), ("cash", 2000), ("card", 5000)])
        self.assertEqual(payment.refund(9000), {"card": 5000, "cash": 2000, "gift_card": 2000})

    def test_earlier_refunds_count(self):
        payment = Payment([("gift_card", 3000), ("card", 5000)])
        payment.refund(4000)
        self.assertEqual(payment.refund(2000), {"card": 1000, "gift_card": 1000})
        self.assertEqual(payment.refund(2000), {"gift_card": 2000})
        self.assertEqual(payment.refundable(), 0)

    def test_too_much_changes_nothing(self):
        payment = Payment([("gift_card", 3000), ("card", 5000)])
        with self.assertRaises(ValueError):
            payment.refund(8001)
        self.assertEqual(payment.refundable(), 8000)
        self.assertEqual(payment.refund(8000), {"card": 5000, "gift_card": 3000})

    def test_too_much_after_a_refund(self):
        payment = Payment([("card", 5000)])
        payment.refund(4000)
        with self.assertRaises(ValueError):
            payment.refund(1001)
        self.assertEqual(payment.refundable(), 1000)

    def test_amount_must_be_positive(self):
        payment = Payment([("card", 5000)])
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                payment.refund(bad)

    def test_same_tender_paid_twice(self):
        payment = Payment([("card", 2000), ("cash", 1000), ("card", 3000)])
        self.assertEqual(payment.refund(5500), {"card": 5000, "cash": 500})
