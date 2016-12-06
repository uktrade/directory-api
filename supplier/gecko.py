from user.models import User as Supplier


def total_registered_suppliers():
    # We're using the Number & Secondary Stat widget (and json format)
    # https://developer-custom.geckoboard.com/#number-and-secondary-stat
    num_registered = Supplier.objects.count()
    return {
        "item": [
            {
              "value": num_registered,
              "text": "Total registered suppliers"
            }
          ]
    }
