# UnoletAPI

Python library to connect with Unolet API

## Project status

This project is in an early stage of development and is not yet fully functional.


## Usage

```py
import unolet

# Connect to the Unolet API
unolet.Unolet.connect("[TOKEN]", "http://localhost:8000")

# Get an invoice by its ID
invoice = unolet.Invoice.get(123)

# Modify and save an invoice
invoice.note = "Modified note"
invoice.save()

# Get a warehouse by its ID
warehouse = unolet.Warehouse.get(3)

# Get a document type by its ID
document_type = unolet.DocumentType.get(5)

# Get a person by its ID
person = unolet.Person.get(743)

# Create and save a new invoice
invoice = unolet.Invoice(
    warehouse=warehouse,
    type=document_type,
    person=person
)
invoice.save()

# Get a product by its ID
product = unolet.Product.get(22)

# Create and save a new product movement
movement = unolet.Movement(
    document=invoice,
    product=product,
    quantity=7,
    price=195.99,
)
movement.save()

```

Now you can easily and efficiently use the Unolet API with this Python library!