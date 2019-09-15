class B(Exception):
    pass


class C(B):
    pass


class D(C):
    pass


for cls in [B, C, D]:
    try:
        raise cls()
    except D:
        print("D")
    except C:
        print("C")
    except B:
        print("B")

try:
    print('test try else')
    # raise C()
except D:
    print('C')
else:
    print('in else')

try:
    raise Exception('spam', 'eggs', 1)
except Exception as inst:
    print(type(inst))  # the exception instance
    print(inst.args)  # arguments stored in .args
    print(inst)  # __str__ allows args to be printed directly,
    # but may be overridden in exception subclasses
    x, y, z = inst.args  # unpack args
    print('x =', x)
    print('y =', y)
    print('z =', z)


# example

def bool_return() -> bool:
    try:
        return True
    finally:  # logic same as java
        return False


print(bool_return())


# example

def divide(x, y):
    try:
        result = x / y
    except ZeroDivisionError:
        print("division by zero!")
    else:
        print("result is", result)
    finally:
        print("executing finally clause")

divide(2, 1)
divide(2, 0)
try:
    divide("2", "1")
except TypeError as error:
    print(error)

print("with clause test")
with open("/temp/tt1.txt") as f, open("/temp/tt2.txt") as f2:
    for line in f:
        print(line, end="")