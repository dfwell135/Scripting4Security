#!/usr/bin/env python3
"""Report the most frequently blocked IPv4 addresses in an ACL CSV export."""

import argparse
import csv
import ipaddress
import json
import re
import sys
from collections import Counter, defaultdict
from urllib.error import URLError
from urllib.request import Request, urlopen


IP_COLUMNS = ("src_ip", "source_ip", "source", "client_ip", "ip_address", "ip", "address")
ACTION_COLUMNS = ("action", "acl_action", "decision", "verdict", "status", "result")
OWNER_COLUMNS = ("owner", "organization", "org", "isp", "as")
LOCATION_COLUMNS = ("location", "city", "region", "country")
DEFAULT_BLOCKED_VALUES = ("deny", "denied", "block", "blocked", "drop", "reject")


def normalize_column(name):
	return re.sub(r"[^a-z0-9]", "", name.casefold())


def find_column(fieldnames, requested, candidates, label):
	normalized_names = {normalize_column(name): name for name in fieldnames}
	if requested:
		result = normalized_names.get(normalize_column(requested))
		if result is None:
			raise ValueError(f"Column '{requested}' not found. Available columns: {', '.join(fieldnames)}")
		return result

	for candidate in candidates:
		result = normalized_names.get(normalize_column(candidate))
		if result is not None:
			return result
	raise ValueError(
		f"Could not identify the {label} column. Available columns: {', '.join(fieldnames)}"
	)


def find_optional_columns(fieldnames, candidates):
	normalized_names = {normalize_column(name): name for name in fieldnames}
	return [normalized_names[normalize_column(candidate)] for candidate in candidates
			if normalize_column(candidate) in normalized_names]


def is_blocked(action, blocked_values):
	action_words = set(re.findall(r"[a-z]+", (action or "").casefold()))
	return bool(action_words.intersection(blocked_values))


def read_blocked_addresses(filename, ip_column, action_column, blocked_values):
	counts = Counter()
	metadata = defaultdict(dict)

	with open(filename, newline="", encoding="utf-8-sig") as csv_file:
		reader = csv.DictReader(csv_file)
		if not reader.fieldnames:
			raise ValueError("The CSV file is empty or has no header row.")

		ip_field = find_column(reader.fieldnames, ip_column, IP_COLUMNS, "IPv4 address")
		action_field = find_column(reader.fieldnames, action_column, ACTION_COLUMNS, "ACL action")
		owner_fields = find_optional_columns(reader.fieldnames, OWNER_COLUMNS)
		location_fields = find_optional_columns(reader.fieldnames, LOCATION_COLUMNS)

		for row in reader:
			if not is_blocked(row.get(action_field), blocked_values):
				continue
			try:
				address = ipaddress.ip_address((row.get(ip_field) or "").strip())
			except ValueError:
				continue
			if not isinstance(address, ipaddress.IPv4Address):
				continue

			ip = str(address)
			counts[ip] += 1
			for label, fields in (("owner", owner_fields), ("location", location_fields)):
				if label not in metadata[ip]:
					value = ", ".join(dict.fromkeys(
						row[field].strip() for field in fields if row.get(field, "").strip()
					))
					if value:
						metadata[ip][label] = value

	return counts, metadata


def lookup_ip_details(ip):
	address = ipaddress.ip_address(ip)
	if not address.is_global:
		return {}

	request = Request(
		f"https://ipwho.is/{ip}",
		headers={"User-Agent": "Scripting4Security-ACL-Analyzer/1.0"},
	)
	with urlopen(request, timeout=5) as response:
		result = json.load(response)
	if not result.get("success"):
		return {}

	connection = result.get("connection") or {}
	location = ", ".join(
		value for value in (result.get("city"), result.get("region"), result.get("country")) if value
	)
	owner = connection.get("org") or connection.get("isp") or connection.get("asn", "")
	return {key: value for key, value in (("location", location), ("owner", owner)) if value}


def main():
	parser = argparse.ArgumentParser(
		description="Count blocked IPv4 addresses in an ACL CSV and report available owner/location data."
	)
	parser.add_argument("csv_file", help="Path to the ACL CSV export")
	parser.add_argument("--ip-column", help="Name of the column containing IPv4 addresses")
	parser.add_argument("--action-column", help="Name of the column containing ACL actions")
	parser.add_argument(
		"--blocked-values",
		default=",".join(DEFAULT_BLOCKED_VALUES),
		help="Comma-separated action words to count as blocked (default: %(default)s)",
	)
	parser.add_argument("--top", type=int, default=10, help="Number of addresses to display (default: 10)")
	parser.add_argument(
		"--lookup", action="store_true",
		help="Look up missing details for public IPs using ipwho.is; this sends those IPs to the service",
	)
	args = parser.parse_args()

	if args.top < 1:
		parser.error("--top must be at least 1")

	blocked_values = {value.strip().casefold() for value in args.blocked_values.split(",") if value.strip()}
	if not blocked_values:
		parser.error("--blocked-values must contain at least one value")

	try:
		counts, metadata = read_blocked_addresses(
			args.csv_file, args.ip_column, args.action_column, blocked_values
		)
	except (OSError, csv.Error, ValueError) as error:
		parser.error(str(error))

	if not counts:
		print("No blocked IPv4 addresses found.")
		return 0

	print(f"Blocked IPv4 addresses: {sum(counts.values())} rows, {len(counts)} unique addresses")
	print(f"{'COUNT':>7}  {'IP ADDRESS':<18}  {'LOCATION':<32}  OWNER")
	print("-" * 90)
	for ip, count in counts.most_common(args.top):
		details = metadata.get(ip, {}).copy()
		if args.lookup and (not details.get("location") or not details.get("owner")):
			try:
				looked_up = lookup_ip_details(ip)
				for key, value in looked_up.items():
					details.setdefault(key, value)
			except (OSError, URLError, TimeoutError, json.JSONDecodeError) as error:
				print(f"Lookup unavailable for {ip}: {error}", file=sys.stderr)
		print(f"{count:>7}  {ip:<18}  {details.get('location', 'unknown'):<32}  {details.get('owner', 'unknown')}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
