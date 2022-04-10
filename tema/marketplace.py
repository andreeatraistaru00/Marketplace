"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread

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
            self.producer_id += 1
            self.products_published[self.producer_id] = 0
            self.products[self.producer_id] = {}
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
           
            res = False
            #Check if producer has space to publish
            if self.products_published[producer_id] <= self.queue_size_per_producer:
                self.products_published[producer_id] += 1
                if product in list(self.products[producer_id].keys()):
                    self.products[producer_id][product] += 1
                else:
                    self.products[producer_id][product] = 1
                res = True

            return res

    def new_cart(self):
        """
        Creates a new cart for the consumer
        :returns an int representing the cart_id
        """
        with self.consumer_lock:
            self.cart_id += 1
            self.carts[self.cart_id] = {}
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

            for producer in list(self.products.keys()):
                if product in list(self.products[producer].keys()):
                    self.products[producer][product] -= 1
                    if (product, producer) in list(self.carts[cart_id].keys()):
                        self.carts[cart_id][(product, producer)] += 1
                    else:
                        self.carts[cart_id][(product, producer)] = 1

                    if self.products[producer][product] == 0:
                        self.products[producer].pop(product, 0)
                    return True

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
            for (product, producer), quantity in self.carts[cart_id].items():
                for _ in range(quantity):
                    self.products_published[producer] -= 1
                    print(f"{currentThread().getName()} bought {product}")
