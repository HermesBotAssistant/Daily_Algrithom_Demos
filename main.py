def add(a, b):
    return a + b

def minus(a, b):
    return a - b

def multiply(a, b):
    return a * b

def devide(a, b):
    if b == 0:
        print("Error: can not device by 0.")
        return None
    return a / b

if __name__ == "__main__":
    print(add(1,2))
    print(minus(10, 1))
    print(multiply(2, 3))
    print(devide(2, 1))
