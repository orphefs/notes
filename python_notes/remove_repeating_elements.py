def remove_repeating_elements(L):
    new_list = []
    L.append(False)
    for prev_item, next_item in zip(L, L[1:]):
        if prev_item == next_item:
            continue
        else:
            new_list.append(prev_item)
    return new_list


def use_remove_repeating_elements():
    L = [1, 1, 2, 1, 1, 1, 2, 4, 3, 1, 1, 1, 4, 4]

    print(remove_repeating_elements(L))


def main():
    use_remove_repeating_elements()


if __name__ == '__main__':
    main()
