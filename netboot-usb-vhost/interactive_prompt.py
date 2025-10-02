#!/usr/bin/env python3

import ipaddress

# Function to prompt for a variable
def prompt_variable(prompt):
    return input(f"{prompt}: ")

# Function to increment an IP address
def increment_ip(ip, increment=1):
    ip_obj = ipaddress.ip_address(ip)
    new_ip = ip_obj + increment

    if new_ip.packed[-1] > 254:
        raise ValueError("Error: IP address incremented beyond .254")

    return str(new_ip)

# Function to generate a list of IP addresses
def generate_ip_list(start_ip, amt):
    try:
        amt = int(amt)
        if amt <= 0:
            raise ValueError
    except ValueError:
        raise ValueError("Error: Amount must be a positive integer.")

    current_ip = start_ip
    ip_list = []

    for _ in range(amt):
        ip_list.append(current_ip)
        current_ip = increment_ip(current_ip)

    return ip_list

# Function to generate a list of strings with incremented numbers
def generate_string_list(base_string, amt):
    try:
        amt = int(amt)
        if amt <= 0:
            raise ValueError
    except ValueError:
        raise ValueError("Error: Amount must be a positive integer.")

    return [f"{base_string}{i:02d}" for i in range(1, amt + 1)]

# Function to create a list of host dictionaries
def create_host_list(base_hostname, start_ip, amt):
    hostnames = generate_string_list(base_hostname, amt)
    ips = generate_ip_list(start_ip, amt)

    return [
        {"hostname": hostname, "ip": ip}
        for hostname, ip in zip(hostnames, ips)
    ]

# Main function to handle prompts and confirmation
def main_prompt():
    while True:
        print("Please provide the following information:")

        try:
            number_of_hosts = int(prompt_variable("NUMBER OF HOSTS"))
            base_hostname = prompt_variable("HOSTNAME BASENAME")
            start_ip = prompt_variable("FIRST IP ADDRESS")
            netmask = prompt_variable("NETMASK")
            gateway = prompt_variable("GATEWAY")
        except ValueError:
            print("Invalid input. Please try again.")
            continue

        host_list = create_host_list(base_hostname, start_ip, number_of_hosts)

        print("\nSummary of your input:")
        print(f"Number of hosts: {number_of_hosts}")
        print(f"Hostnames and IPs:")
        for host in host_list:
            print(f"  Hostname: {host['hostname']}, IP: {host['ip']}")
        print(f"Netmask: {netmask}")
        print(f"Gateway: {gateway}")

        confirmation = input("Is this information correct? (y/n/q): ").strip().lower()

        if confirmation == 'y':
            print("Confirmed. Proceeding with the installation.")
            break
        elif confirmation == 'n':
            print("Restarting prompts.")
        elif confirmation == 'q':
            print("Quitting installation.")
            exit(1)
        else:
            print("Invalid response. Please enter 'y', 'n', or 'q'.")

if __name__ == "__main__":
    main_prompt()

