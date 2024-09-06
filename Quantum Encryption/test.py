import webbrowser
import time

def annoying_malware():
    while True:
        # Open a browser to a silly website
        webbrowser.open("https://www.annoyingwebsite.com")
        # Sleep for 10 seconds before opening again
        time.sleep(10) # DO NOT CHANGE TO 1 FOR WHATEVER REASON PLEASE

if __name__ == "__main__":
    annoying_malware()
