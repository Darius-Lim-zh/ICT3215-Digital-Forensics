def add_numbers(a, b):
    print(f"Input for addition: a = {a}, b = {b}")
    result = a + b
    print(f"Output of addition: {result}\n")
    return result

def subtract_numbers(a, b):
    print(f"Input for subtraction: a = {a}, b = {b}")
    result = a - b
    print(f"Output of subtraction: {result}\n")
    return result

def multiply_numbers(a, b):
    print(f"Input for multiplication: a = {a}, b = {b}")
    result = a * b
    print(f"Output of multiplication: {result}\n")
    return result

def divide_numbers(a, b):
    if b == 0:
        print("Error: Division by zero is undefined.\n")
        return None
    print(f"Input for division: a = {a}, b = {b}")
    result = a / b
    print(f"Output of division: {result}\n")
    return result

def factorial(n):
    print(f"Input for factorial: n = {n}")
    if n == 0 or n == 1:
        return 1
    else:
        result = n * factorial(n - 1)
        print(f"Output of factorial for n = {n}: {result}\n")
        return result

# Sample usage of the functions

a = 10
b = 5
n = 4

# Perform operations
add_result = add_numbers(a, b)
subtract_result = subtract_numbers(a, b)
multiply_result = multiply_numbers(a, b)
divide_result = divide_numbers(a, b)

# Perform recursive factorial calculation
factorial_result = factorial(n)

# Final output
print("Results:")
print(f"Addition: {add_result}")
print(f"Subtraction: {subtract_result}")
print(f"Multiplication: {multiply_result}")
print(f"Division: {divide_result}")
print(f"Factorial: {factorial_result}")
