
class t:
    def __init__(self):
        raise ValueError("test")


def func():
    try:
        T = t()
    except ValueError:
        print("error catched")

    return T or None



print(func())