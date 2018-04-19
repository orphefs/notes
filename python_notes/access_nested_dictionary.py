def access_nested_dictionary(d):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from access_nested_dictionary(v)
    elif hasattr(d, '__iter__') and not isinstance(d, str):
        for item in d:
            yield from access_nested_dictionary(item)
    elif isinstance(d, str):
        yield d
    else:
        yield d


def use_access_nested_dictionary():
    d = {
        "user": 10,
        "time": "2017-03-15T14:02:49.301000",
        "metadata": [
            {"foo": "bar"},
            "some_string"
        ]
    }

    for item in access_nested_dictionary(d):
        print(item)


def main():
    use_access_nested_dictionary()


if __name__ == '__main__':
    main()
