# UnoletAPI

Python library to connect with Unolet API

![image](https://github.com/unolet1/unolet-python-api/assets/44853160/785fb5b3-537a-45a0-921f-58746bb2679f)

## Project status

This project is in an early stage of development and is not yet fully functional.

## Instalation

To install the UnoletAPI library, you can use pip:


```sh
pip install unolet
```


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

## Contributing
We welcome contributions to improve this library. Please fork the repository and submit pull requests for review.

## Support
For any questions or issues, please visit the [Unolet Support Page](https://unolet.app/help/).

### Links
* [Unolet Official Website](https://www.unolet.com)
* [Unolet Documentation](https://unolet.app/tools/#python)

## License
This project is licensed under the MIT License. See the LICENSE file for more information.
