"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread
import unittest
import logging
import time
from logging.handlers import RotatingFileHandler
from tema.product import Coffee, Tea

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('$asctime : $levelname : $name : $message', style='$')
handler = RotatingFileHandler('marketplace.log', maxBytes=20000, backupCount=5)
handler.setFormatter(formatter)

formatter.converter = time.gmtime

logger.addHandler(handler)


class TestMarketplace(unittest.TestCase):
    """
    Class used for unittestting
    """
    def setUp(self):
        """
        Initializes the marketplace class
        """
        self.queue_size_per_producer = 15
        self.marketplace = Marketplace(self.queue_size_per_producer)
        self.marketplace.producer_id = 3
        self.marketplace.cart_id = 5
        self.products = [Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM'),
                        Tea(name='Linden', price=9, type='Herbal'),
                        Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM'),
                        Tea(name='Wild Cherry', price=5, type='Black'),
                        Tea(name='Cactus fig', price=3, type='Green'),
                        Coffee(name='Ethiopia', price=10, acidity=5.09, roast_level='MEDIUM')]


    def test_register_producer(self):
        """
        Checks that the id returned is increased correctly
        """
        self.assertIsNotNone(self.marketplace.register_producer())
        self.assertEqual(self.marketplace.register_producer(), 5)

    def test_publish(self):
        """
        Checks that the products list has added the right products
        """
        producer_id = self.marketplace.register_producer()
        dict1 = {producer_id: {self.products[0]: 2}}
        self.marketplace.products[producer_id][self.products[0]] = 1

        self.assertTrue(self.marketplace.publish(producer_id, self.products[0]))
        self.assertDictEqual(self.marketplace.products, dict1)

    def test_new_cart(self):
        """
        Checks that it returns an increased value for the cart id
        """
        self.assertIsNotNone(self.marketplace.new_cart())
        self.assertEqual(self.marketplace.new_cart(), 7)

    def test_add_to_cart(self):
        """
        Checks that the cart will have the correct products
        """
        producer_id = self.marketplace.register_producer()
        self.marketplace.publish(producer_id, self.products[0])
        self.marketplace.publish(producer_id, self.products[1])
        cart_id = self.marketplace.new_cart()
        carts = {cart_id: {(self.products[1], producer_id): 1}}

        self.assertFalse(self.marketplace.add_to_cart(cart_id, self.products[3]))
        self.assertTrue(self.marketplace.add_to_cart(cart_id, self.products[1]))
        self.assertDictEqual(self.marketplace.carts[cart_id], carts[cart_id])

    def test_remove_from_cart(self):
        """
        Checks that the cart will have the correct products
        """
        producer_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()

        self.marketplace.publish(producer_id, self.products[0])
        self.marketplace.publish(producer_id, self.products[1])
        self.marketplace.publish(producer_id, self.products[1])

        self.marketplace.add_to_cart(cart_id, self.products[0])
        self.marketplace.add_to_cart(cart_id, self.products[1])
        self.marketplace.add_to_cart(cart_id, self.products[1])
        self.marketplace.remove_from_cart(cart_id, self.products[0])
        carts = {cart_id: {(self.products[1], producer_id): 2}}

        self.assertDictEqual(self.marketplace.carts[cart_id], carts[cart_id])

    def test_place_order(self):
        """
        Checks if after place order the producer has more space in his queue
        """
        producer_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()

        self.marketplace.publish(producer_id, self.products[0])
        self.marketplace.publish(producer_id, self.products[1])
        self.marketplace.publish(producer_id, self.products[1])

        self.marketplace.add_to_cart(cart_id, self.products[0])
        self.marketplace.add_to_cart(cart_id, self.products[1])
        self.marketplace.add_to_cart(cart_id, self.products[1])
        self.marketplace.remove_from_cart(cart_id, self.products[0])
        self.marketplace.place_order(cart_id)

        self.assertEqual(self.marketplace.products_published[producer_id], 1)

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor
        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.consumer_lock = Lock()
        self.producer_lock = Lock()
        self.products = {} #dictionary that contains (producer_id, (products, quantity))
        self.carts = {} #dictionary of carts (cart_id, ((product, producer_id), quantity))
        self.products_published = {} #dictionary with (producer_id, products_published)
        self.producer_id = -1
        self.cart_id = -1

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.producer_lock:
            logger.info('[OLD]Last producer id:%d', self.producer_id)
            self.producer_id += 1
            self.products_published[self.producer_id] = 0
            self.products[self.producer_id] = {}
            logger.info('[UPDATE]New producer id:%d', self.producer_id)
            return self.producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace
        :type producer_id: String
        :param producer_id: producer id
        :type product: Product
        :param product: the Product that will be published in the Marketplace
        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        with self.producer_lock:
            logger.info('[INPUT]Producer_id: %s and Product: %s', producer_id, product)

            res = False
            #Check if producer has space to publish
            if self.products_published[producer_id] <= self.queue_size_per_producer:
                self.products_published[producer_id] += 1
                if product in list(self.products[producer_id].keys()):
                    self.products[producer_id][product] += 1
                else:
                    self.products[producer_id][product] = 1
                res = True

            logger.info('[OUTPUt]Method returns: %r', res)
            return res

    def new_cart(self):
        """
        Creates a new cart for the consumer
        :returns an int representing the cart_id
        """
        with self.consumer_lock:
            logger.info('[OLD]:Cart_id: %d', self.cart_id)
            self.cart_id += 1
            self.carts[self.cart_id] = {}
            logger.info('[UPDATE]:Cart_id: %d', self.cart_id)
            return self.cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns
        :type cart_id: Int
        :param cart_id: id cart
        :type product: Product
        :param product: the product to add to cart
        :returns True or False. If the caller receives False, it should wait and then try again
        """
        with self.consumer_lock:
            logger.info('[INPUT]Cart_id: %d and Product: %s', cart_id, product)

            for producer in list(self.products.keys()):
                if product in list(self.products[producer].keys()):
                    self.products[producer][product] -= 1
                    if (product, producer) in list(self.carts[cart_id].keys()):
                        self.carts[cart_id][(product, producer)] += 1
                    else:
                        self.carts[cart_id][(product, producer)] = 1

                    if self.products[producer][product] == 0:
                        self.products[producer].pop(product, 0)
                    logger.info('[OUTPUT]Method returns: True')
                    return True

        logger.info('[OUTPUT]Method returns: False')
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.
        :type cart_id: Int
        :param cart_id: id cart
        :type product: Product
        :param product: the product to remove from cart
        """
        with self.consumer_lock:
            logger.info('[INPUT]Cart_id: %d and Product: %s', cart_id, product)
            for (prod, producer_id) in list(self.carts[cart_id].keys()):
                if prod == product:
                    self.carts[cart_id][(product, producer_id)] -= 1
                    if self.carts[cart_id][(product, producer_id)] == 0:
                        self.carts[cart_id].pop((product, producer_id), 0)

                    if product in list(self.products[producer_id].keys()):
                        self.products[producer_id][product] += 1
                    else:
                        self.products[producer_id][product] = 1
                    break

    def place_order(self, cart_id):#
        """
        Return a list with all the products in the cart.
        :type cart_id: Int
        :param cart_id: id cart
        """
        with self.consumer_lock:
            logger.info('[INPUT]Place order for cart_id: %d', cart_id)
            for (product, producer), quantity in self.carts[cart_id].items():
                for _ in range(quantity):
                    self.products_published[producer] -= 1
                    print(f"{currentThread().getName()} bought {product}")
