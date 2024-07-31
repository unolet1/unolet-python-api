"""
Unolet API Client Library

This module provides an interface to interact with the Unolet ERP system via its
API. It includes various classes representing different entities in the Unolet
ERP system such as documents, invoices, purchases, quotations, and more.

Public Classes:
    - Unolet
    - Company
    - DocumentType
    - Document
    - Invoice
    - Purchase
    - PurchaseOrder
    - Quotation
    - Movement
    - NCF
    - AuthorizationNCF
    - Person
    - Product
    - Transaction
    - Warehouse

Example:
    from unolet import Unolet

    # Initialize the Unolet API client
    Unolet.connect("your_token_here", "your_unolet_base_url_here", "v1")
"""

__version__ = "0.0.2"

from unolet.api import UnoletAPI as Unolet
from unolet.erp import (
    DocumentType,
    Document,
    Invoice,
    Purchase,
    PurchaseOrder,
    Quotation,
    Person,
    Product,
    Movement,
    NCF,
    AuthorizationNCF,
    Transaction,
    Warehouse,
)


__all__ = [
    "Unolet",
    "Company",
    "DocumentType",
    "Document",
    "Invoice",
    "Purchase",
    "PurchaseOrder",
    "Quotation",
    "Movement",
    "NCF",
    "AuthorizationNCF",
    "Person",
    "Product",
    "Transaction",
    "Warehouse",
]
