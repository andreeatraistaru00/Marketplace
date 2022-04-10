"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    def add_operation(self, quantity, cart_id, product):
        """
        Class that calls add for all the items requestes
        """
        for _ in range(quantity):
            while not self.marketplace.add_to_cart(cart_id, product):
                time.sleep(self.retry_wait_time)

    def remove_operation(self, quantity, cart_id, product):
        """
        Class that calls remove for all the items requestes
        """
        for _ in range(quantity):
            self.marketplace.remove_from_cart(cart_id, product)

    def run(self):
        for cart in self.carts:
            id_cart = self.marketplace.new_cart()
            for operation in cart:
                if operation["type"] == "add":
                    self.add_operation(operation["quantity"], id_cart, operation["product"])
                else:
                    self.remove_operation(operation["quantity"], id_cart, operation["product"])

            self.marketplace.place_order(id_cart)
