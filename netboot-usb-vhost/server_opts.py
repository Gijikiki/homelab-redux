#!/bin/env python3

class ServerOpts:
    def __init__(self):
        self.generated_hosts = []

    def print_pretty_list(self):
        for host in self.generated_hosts:
            print(f"{host['name']}:")
            print(f"  ip: {host['ip']}")
            print(f"  gateway: {host['gateway']}")
            print(f"  netmask: {host['netmask']}\n")

    def prompt_for_hosts(self):
        while True:
            base_name = input("Enter the base name for the servers: ")
            first_ip = input("Enter the first IP address: ")
            gateway = input("Enter the gateway: ")
            netmask = input("Enter the netmask: ")
            num_servers = int(input("Enter the number of servers: "))

            ip_parts = list(map(int, first_ip.split('.')))

            self.generated_hosts = []
            for i in range(num_servers):
                current_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3] + i}"
                self.generated_hosts.append({
                    "name": f"{base_name}{i + 1:02}",
                    "ip": current_ip,
                    "gateway": gateway,
                    "netmask": netmask
                })

            self.print_pretty_list()

            confirmation = input("Confirm these settings? (y/n/q): ").lower()
            if confirmation == 'y':
                break
            elif confirmation == 'q':
                print("Exiting.")
                exit()
            elif confirmation == 'n':
                print("Redoing prompt.")

        self.print_pretty_list()

if __name__ == "__main__":
    # Example Usage
    preseed_values = ServerOpts()
    preseed_values.prompt_for_hosts()

