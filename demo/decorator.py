import functools


def singleton(cls):
    """Make a class a Singleton class (only one instance)"""

    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    # 这是因为 Python 中的函数是一等公民，即函数可以像变量一样被传递、赋值、作为参数和返回值等。因此，当定义一个装饰器函数时，实际上是在定义一个函数对象，并将其作为参数传递给被装饰的函数或类。
    # 当装饰器函数被调用时，它会返回一个新的函数对象，该函数对象包含装饰器的功能。在本例中，装饰器函数 singleton 返回的是一个函数对象 wrapper_singleton，它具有单例模式的功能。因此，wrapper_singleton.instance = None 语句只会在 singleton 函数内部被调用一次，即在定义 wrapper_singleton 函数时执行。
    # 一旦返回 wrapper_singleton 函数对象后，wrapper_singleton.instance 属性就会被初始化为 None。在以后的每次调用 wrapper_singleton 函数时，都会检查 wrapper_singleton.instance 属性是否存在，并根据其是否为 None 来判断是否要创建新的实例。
    # 因此，在每次创建类的时候并不会调用 wrapper_singleton.instance = None 语句。只有在装饰器函数被定义时，才会初始化 wrapper_singleton.instance 属性为 None，以确保第一次调用 wrapper_singleton 函数时能够成功创建一个新的实例。
    return wrapper_singleton


@singleton
class TheOne:
    pass


the_one = TheOne()
print(id(the_one))
the_two = TheOne()
print(id(the_two))
