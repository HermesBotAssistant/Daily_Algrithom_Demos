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
    # Test cases
    print("--- Running Tests ---")
    print(f"1 + 2 = {add(1, 2)}")
    print(f"10 - 5 = {minus(10, 5)}")
    print(f"3 * 4 = {multiply(3, 4)}")
    print(f"10 / 2 = {devide(10, 2)}")
    print(f"5 / 0 = {devide(5, 0)}")
    print("--- Tests Finished ---")