# This class demonstrates an overloaded __repr__ method, which produces a string that takes in the property names
# but not method names. 

import inspect


class Foo:
    def __init__(self, var_1, var_2):
        self._var_1 = var_1
        self._var_2 = var_2

    @property
    def var_1(self):
        return self._var_1

    @property
    def var_2(self):
        return self._var_2

    def bar(self):
        pass

    def __repr__(self):
        class_name = self.__class__.__name__
        members = ", ".join(["{} = {}".format(property_name, getattr(self, property_name))
                             for (property_name, property_value) in
                             inspect.getmembers(self.__class__, lambda x: isinstance(x, property))])

        return "{}({})".format(class_name, members)


if __name__ == '__main__':
    foo = Foo(1, 2)
    print(foo)
