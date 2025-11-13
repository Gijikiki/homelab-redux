#!/bin/env python3

class ServerOpts:
    def __init__(self):
        self.generated_hosts = []
        self.prompt_for_hosts()

    def print_pretty_list(self):
        print("--- Servers ---")
        for host in self.generated_hosts:
            print(f"  - {host['name']}.{host['domain']}:")
            print(f"      ip: {host['ip']}")
        print("--- Domain ---")
        print(f" - gateway: {self.generated_hosts[0]['gateway']}")
        print(f" - netmask: {self.generated_hosts[0]['netmask']}")
        print(f" - nameserver: {self.generated_hosts[0]['dns']}")

    def get_default_gateway(self, first_ip):
        return f"{'.'.join(first_ip.split('.')[:-1])}.1"

    def get_hosts(self):
        return self.generated_hosts

    def prompt_for_hosts(self):
        while True:
            base_name = input("Enter the base name for the servers: ")
            first_ip = input("Enter the first IP address: ")
            default_gw = self.get_default_gateway(first_ip)
            gateway = input(f"Enter the gateway (default: {default_gw}): ") or default_gw
            netmask = input("Enter the netmask (default: 255.255.255.0): ") or "255.255.255.0"
            dns = input(f"Enter the name servers (default: {gateway}): ") or gateway
            domain = input("Enter the domain: (default: home.arpa): ") or "home.arpa"
            num_servers = int(input("Enter the number of servers: "))

            ip_parts = list(map(int, first_ip.split('.')))

            self.generated_hosts = []
            for i in range(num_servers):
                current_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3] + i}"
                self.generated_hosts.append({
                    "name": f"{base_name}{i + 1:02}",
                    "config": f"preseed-{base_name}{i + 1:02}.cfg",
                    "ip": current_ip,
                    "gateway": gateway,
                    "netmask": netmask,
                    "dns": dns,
                    "domain": domain,
                })

            self.print_pretty_list()

            confirmation = input("Confirm these settings? (y/n/q): ").lower()
            if confirmation == 'y':
                break
            elif confirmation == 'q':
                print("Exiting.")
                exit(1)
            elif confirmation == 'n':
                print("Redoing prompt.")


if __name__ == "__main__":
    # Example Usage
    preseed_values = ServerOpts()
