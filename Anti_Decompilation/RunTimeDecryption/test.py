# test_cython.py

def add_numbers(a, b):
    """Adds two numbers."""
    return a + b

def factorial(n):
    """Returns the factorial of a number using recursion."""
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

def reverse_string(s):
    """Reverses a given string."""
    return s[::-1]

def sum_list_elements(lst):
    """Returns the sum of all elements in a list."""
    total = 0
    for num in lst:
        total += num
    return total

def count_vowels(s):
    """Counts the number of vowels in a string."""
    vowels = "aeiouAEIOU"
    count = 0
    for char in s:
        if char in vowels:
            count += 1
    return count

def main():
    print("Addition of 10 and 20:", add_numbers(10, 20))
    print("Factorial of 5:", factorial(5))
    print("Reversed string 'hello':", reverse_string("hello"))
    print("Sum of list [1, 2, 3, 4, 5]:", sum_list_elements([1, 2, 3, 4, 5]))
    print("Vowel count in 'This is a test string':", count_vowels("This is a test string"))

if __name__ == '__main__':
    main()