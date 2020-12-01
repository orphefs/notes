def explode_nested_list(l: list):
    exploded_list = []
    for item in l:
        if isinstance(item, list):
            exploded_list += explode_nested_list(item)
        else:
            exploded_list.append(item)
    return exploded_list

explode_nested_list([1,2,[3,[4, [5,6,7]]]])
