import unittest

from store.refunds import Payment


class TaskTest(unittest.TestCase):
    def test_card_before_gift_card(self):
        payment = Payment([("gift_card", 3000), ("card", 5000)])
        self.assertEqual(payment.refund(4000), {"card": 4000})
        self.assertEqual(payment.refundable(), 4000)
