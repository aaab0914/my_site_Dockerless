import re
from collections import Counter


def analyze_logs(log_file):
    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    with open(log_file, encoding='utf-8') as log:
        ips = [match.group(1) for line in log if (match := ip_pattern.search(line))]

    print("Most frequent IP addresses:")
    for ip, count in Counter(ips).most_common(10):
        print(f"  {ip}: {count} requests")
