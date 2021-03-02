def deep_compare(dict2, dict1):
    # Match all fields in dict1 to dict2.  Additional fields in dict2 are ignored
    for key, val in dict1.items():
        if isinstance(val, dict) and isinstance(dict2.get(key), dict):
            if not deep_compare(val, dict2.get(key)):
                raise AssertionError('Comparison dict failure - ', key, val)
                return False
        if val != dict2.get(key):
            raise AssertionError('Comparison failure - ', key, val)
            return False
    return True
