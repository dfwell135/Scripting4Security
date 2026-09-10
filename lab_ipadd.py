#!/usr/bin/env python3
import ipaddress
from collections import Counter

def load_ip_addresses(filename):
    """Load IP addresses from a file into a list"""
    try:
        with open(filename) as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return []
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []

def find_matching_ips(ip_list, ip_range):
    """Find IP addresses in the list that match the given IP range"""
    return [ip for ip in ip_list if ip.startswith(ip_range)]

def main():
    filename = input("Enter the filename containing IP addresses: ")
    ip_list = load_ip_addresses(filename)

    if ip_list:
        partial_ip = input("Enter the partial IP address to match (e.g., '192.168.1'): ")
        matching_ips = find_matching_ips(ip_list, partial_ip)

        if matching_ips:
            count = Counter(matching_ips)
            print(f"\nMatching IP addresses for '{partial_ip}':")
            for ip in matching_ips:
                print(f"- {ip} (appears {count[ip]} times)")
        else:
            print(f"No matching IP addresses found for '{partial_ip}'.")

if __name__ == "__main__":
    main()