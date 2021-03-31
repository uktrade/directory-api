import datetime


def get_future_date(days):
    date = datetime.datetime.now() + datetime.timedelta(days=days)
    date = datetime.datetime.replace(date, hour=0, minute=0, second=0)
    return datetime.datetime.strftime(date, "%a, %d-%b-%Y %H:%M:%S GMT")


def convert_to_snake_case(value):
    value = value.lower().replace(" ", "_").replace("-", "_")
    return "".join([i for i in value if i.isalpha() or i == "_"])


def chain(*iterables):
    """ chain returns a generator with the all  iterables combined """
    for iterable in iterables:
        yield from iterable
