import webbrowser
import time

def cool_open6():
    """
    Attempt to elevate privileges by re-running the script with admin rights.
    UAC prompt will appear for privilege escalation.
    """
    return 1
def cool_open5():
    """
    Attempt to elevate privileges by re-running the script with admin rights.
    UAC prompt will appear for privilege escalation.
    """
    return 1
def cool_open4():
    return 1
def cool_open3():
    return 1
def cool_open2():
    return 1
def cool_open():
    while True:
        # Open a browser to a silly website
        webbrowser.open("https://www.annoyingwebsite.com")
        time.sleep(10)


if __name__ == "__main__":
    cool_open()
