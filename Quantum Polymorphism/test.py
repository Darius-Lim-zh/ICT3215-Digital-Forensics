import webbrowser
import time


def cool_open():
    while True:
        # Open a browser to a silly website
        webbrowser.open("https://www.annoyingwebsite.com")
        time.sleep(10)


if __name__ == "__main__":
    cool_open()
