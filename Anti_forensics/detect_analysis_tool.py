import psutil


def detect_analysis_tools():
    """
    Detect if common forensic or analysis tools (e.g., Wireshark, Procmon) are running.
    """
    analysis_tools = ["procmon", "wireshark", "fiddler", "tcpview", "autoruns"]

    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() in analysis_tools:
            print(f"Analysis tool detected: {proc.info['name']}")
            return True
    return False


if detect_analysis_tools():
    print("Forensic tool detected! Taking anti-forensic action.")
    exit(1)
