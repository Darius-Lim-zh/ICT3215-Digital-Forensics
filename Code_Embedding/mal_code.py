import random


def injected_function():
    print('This function was injected into the script.')
    magic_number = random.randint(1, 200)
    print(magic_number)
    if magic_number > 50:
        return 0
    else:
        return 1
