"""
Establishes connection with Unolet's customized ERP system.

"""

from unolet.models import UnoletResource


class Document(UnoletResource):
    pass


class Invoice(Document):
    endpoint = "invoice"