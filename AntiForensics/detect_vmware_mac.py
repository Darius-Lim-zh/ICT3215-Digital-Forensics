import psutil

def print_results(found, msg):
    """Print the results of the MAC address check."""
    if found:
        print(f"[FOUND] {msg}")
    else:
        print(f"[NOT FOUND] {msg}")

def check_mac_addr(mac_prefix):
    """Check if any network interface MAC address starts with the given prefix."""
    # Iterate through all network interfaces
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Check if the address family is AF_LINK (MAC)
            if addr.family == psutil.AF_LINK:
                mac = addr.address
                # Check if the MAC address starts with the given prefix
                if mac.startswith(mac_prefix):
                    return True
    return False

def vmware_mac():
    """Check for VMWare NIC MAC addresses."""
    # VMWare blacklisted MAC addresses
    mac_addresses = [
        ("\x00\x05\x69", "00:05:69"),  # VMWare, Inc.
        ("\x00\x0C\x29", "00:0c:29"),  # VMWare, Inc.
        ("\x00\x1C\x14", "00:1C:14"),  # VMWare, Inc.
        ("\x00\x50\x56", "00:50:56"),  # VMWare, Inc.
    ]

    # Check each MAC address prefix one by one
    for mac_prefix, mac_display in mac_addresses:
        msg = f"Checking MAC starting with {mac_display}"
        if check_mac_addr(mac_prefix):
            print_results(True, msg)
        else:
            print_results(False, msg)


def call_detect_vmware_mac():
    vmware_mac()

# if __name__ == "__main__":
#     vmware_mac()
