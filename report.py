import re
import matplotlib.pyplot as plt
import argparse

total_requests = 0
endpoint_counts = {}
endpoint_times = {}
unique_users = set()
users_by_year = {}

timetable_total = 0
algo_counts = {"backtracking": 0, "iterative": 0}

with open("timetable.log", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

for line in lines:
    request_match = re.match(
        r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} \[\S+\] (GET|POST) (\S+) (\d{3}) ([\d.]+)µs$', line)

    if request_match:
        method = request_match.group(1)
        endpoint = request_match.group(2)
        status_code = request_match.group(3)
        resp_time_us = float(request_match.group(4))
        resp_time_ms = resp_time_us / 1000.0

        total_requests += 1

        if endpoint not in endpoint_counts:
            endpoint_counts[endpoint] = 0
            endpoint_times[endpoint] = []
        endpoint_counts[endpoint] += 1
        endpoint_times[endpoint].append(resp_time_ms)

    elif "router:" in line:
        user_match = re.search(r'router:\s+(\S+)(?:\s+\[([^\]]+)\])?', line)
        if user_match:
            endpoint = user_match.group(1)
            user_id = user_match.group(2)
            if endpoint not in endpoint_counts:
                endpoint_counts[endpoint] = 0
                endpoint_times[endpoint] = []
            endpoint_counts[endpoint] += 1

            if user_id:
                unique_users.add(user_id)
                year = user_id[:4]
                users_by_year[year] = users_by_year.get(year, 0) + 1

    if "Heuristic Backtracking Strategy" in line:
        algo_counts["backtracking"] += 1
        timetable_total += 1
    elif "Iterative Random Sampling Strategy" in line:
        algo_counts["iterative"] += 1
        timetable_total += 1

print("Report")
print(f"\nTotal API requests: {total_requests}")

print("\nEndpoint Popularity")
for ep, count in endpoint_counts.items():
    print(f"{ep}: {count} requests")

print("\nEndpoint Performance")
for ep, times in endpoint_times.items():
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        print(f"{ep}: Average={avg_time:.4f} ms, Max={max_time:.4f} ms")

print("\nUsers")
print(f"Total unique users: {len(unique_users)}")
for year, count in sorted(users_by_year.items()):
    print(f"Year {year}: {count} users")

print("\nTimetable Generation Insights")
print(f"Total timetables generated: {timetable_total}")
print(f"Backtracking used: {algo_counts['backtracking']} times")
print(f"Iterative random sampling used: {algo_counts['iterative']} times")

endpoints = list(endpoint_counts.keys())
request_counts = [endpoint_counts[ep] for ep in endpoints]

avg_times = []
for ep in endpoints:
    times = endpoint_times.get(ep, [])
    avg_times.append(sum(times) / len(times) if times else 0)

years = sorted(users_by_year.keys())
user_counts = [users_by_year[yr] for yr in years]

plt.subplot(2, 3, 1)
plt.bar(endpoints, request_counts, color='blue')
plt.xticks(rotation=45, ha='right')
plt.title('API Endpoint Popularity (Number of Requests)')
plt.ylabel('Number of Requests')
plt.tight_layout()
plt.show()

plt.subplot(2, 3, 2)
plt.bar(endpoints, avg_times, color='red')
plt.xticks(rotation=45, ha='right')
plt.title('Average Response Time per Endpoint (ms)')
plt.ylabel('Avg Response Time (ms)')
plt.tight_layout()
plt.show()

plt.subplot(2, 3, 3)
plt.bar(years, user_counts, color='green')
plt.title('Number of Users by Year')
plt.xlabel('Year')
plt.ylabel('Number of Users')
plt.tight_layout()
plt.show()

parser = argparse.ArgumentParser(description='Generate parts of timetable log report.')
parser.add_argument('logfile', help='Path to the timetable log file')
parser.add_argument('--endpoints', action='store_true', help='Show endpoint popularity')
parser.add_argument('--performance', action='store_true', help='Show endpoint performance metrics')
parser.add_argument('--users', action='store_true', help='Show user statistics')
parser.add_argument('--timetable', action='store_true', help='Show timetable generation insights')

args, unknown = parser.parse_known_args()
