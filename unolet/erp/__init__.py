"""
Establishes connection with Unolet's customized ERP system.

"""

from unolet.models import UnoletResource


class Movement(UnoletResource):
    _endpoint = "movement"


class Document(UnoletResource):
    _endpoint = None


class Invoice(Document):
    _endpoint = "invoice"


class Purchase(Document):
    _endpoint = "purchase"


class PurchaseOrder(Document):
    _endpoint = "purchaseorder"


class Quotation(Document):
    _endpoint = "quotation"


class Person(UnoletResource):
    _endpoint = "person"


class Product(UnoletResource):
    _endpoint = "product"


class Transaction(UnoletResource):
    _endpoint = "transaction"


class NCF(UnoletResource):
    _endpoint = "ncf"


class AuthorizationNCF(UnoletResource):
    _endpoint = "authorizationncf"