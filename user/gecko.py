from user.models import User


def total_registered_users():
    # We're using the Number & Secondary Stat widget (and json format)
    # https://developer-custom.geckoboard.com/#number-and-secondary-stat
    num_registered = User.objects.count()
    return {
        "item": [
            {
              "value": num_registered,
              "text": "Total registered users"
            }
          ]
    }
