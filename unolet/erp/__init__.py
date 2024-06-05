"""
Establishes connection with Unolet's customized ERP system.

"""

from unolet.models import UnoletResource


class Document(UnoletResource):
    _endpoint = None


class Invoice(Document):
    _endpoint = "invoice"