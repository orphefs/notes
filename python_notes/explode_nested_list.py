def explode_nested_list(list_like_item):
    exploded_list = []
    if isinstance(list_like_item, list):
        for item in list_like_item:
            if isinstance(item, list):
                exploded_list += explode_nested_list(item)
            else:
                exploded_list.append(item)
    elif isinstance(list_like_item, str):
        exploded_list.append(list_like_item)
    return exploded_list

explode_nested_list([1,2,[3,[4, [5,6,7]]]])
explode_nested_list(["blah", "blom"])
explode_nested_list(['Roasted Chili Corn Salsa', ['Fajita Vegetables', 'Rice', 'Black Beans', 'Cheese', 'Sour Cream']])
