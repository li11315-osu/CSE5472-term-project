# This program simulates normal user traffic on our DNS server
# by sending queries for our domain name to a range of public resolvers
# and measures the speed and success rates of the requests

# Currently, it sends requests at a constant rate and cycles through the
# list of resolvers in order to keep it relatively deterministic

# Use the --file option to store the results as JSON in the specified file path
# otherwise the JSON gets printed to the console

import subprocess
import threading
import argparse
import time
import json

# Config

domain = "www.dummy-site-for-dns-ddos-testing.com" # Only one subdomain of interest

resolvers = open("resolvers-trusted.txt", 'r').read().splitlines()
# Original source of resolver list: https://github.com/trickest/resolvers/blob/main/resolvers-trusted.txt
# IPs excluded: 159.89.120.99, 89.233.43.71, 91.239.100.100 (consistently don't respond), 77.88.8.8, 77.88.8.1 (Yandex - don't want to send traffic to Russia)

num_requests = len(resolvers) * 3
interval = 100 # In milliseconds

# Test results, indexed by corresponding request number
# Fields that will be recorded:
# - index: sequence number (starting from 0)
# - resolver: IP address of resolver used
# - start_time: time of initiating query, relative to test start, in ms
# - end_time: time of query finishing, relative to test start, in ms, set to None in case of timeout
# - response_time: end_time - start_time, set to None in case of timeout
# - success: whether or not query was able to get response, based on dig's return code
results = [None] * num_requests

# Timing
test_start_time = time.time()
def get_ms_since_test_start():
    return int((time.time() - test_start_time) * 1000)
def get_timestamp_str():
    return "[t=" + str(get_ms_since_test_start()) + "ms]"

# Process of sending and measuring a single query
def do_request(index : int):
    # Figure out which resolver to use
    # Use dig to look up the domain using that resolver
    # Record the response time and success status in the results object

    resolver = get_resolver(index)
    results[index] = {"index": index, "resolver": resolver, "start_time": None, "end_time": None, "response_time": None, "success": False} # Default values populated for case of timeout

    print(get_timestamp_str() + " Starting query " + str(index) + " (resolver: " + resolver + ")")

    args = ["dig", "@" + resolver, domain] # To be passed into command line
    start_time = get_ms_since_test_start()
    results[index]["start_time"] = start_time # Record start time alongside response time for additional context when analyzing results
    dig_result = subprocess.run(args)
    end_time = get_ms_since_test_start()

    response_time = end_time - start_time
    results[index]["end_time"] = end_time
    results[index]["response_time"] = response_time

    exit_code = dig_result.returncode # If response times out, dig will exit with code 9 after 15 seconds
    success = exit_code == 0
    results[index]["success"] = success
    print(get_timestamp_str() + " Finished attempting query " + str(index) + " (resolver: " + resolver + ")" + " in " + str(response_time) + "ms, dig exited with code " + str(exit_code))

# Subtasks
def get_resolver(index : int):
    return resolvers[index % len(resolvers)]


# Main routine:
# Make an async / fire-and-forget call to initiate a query and measurement without waiting for the response
# Wait for the specified interval, and then repeat
# Continue until reaching specified number of queries
# Wait all queries to either finish or timeout
# Report the current state of the results object and terminate
def main(args):
    threads = [None] * num_requests

    for index in range(num_requests):
        if index > 0:
            time.sleep(interval / 1000)
        threads[index] = threading.Thread(target=do_request, args=(index,))
        threads[index].start()

    print(get_timestamp_str() + " All queries started, waiting for response or timeout")

    for index in range(num_requests):
        threads[index].join()

    print()
    print(get_timestamp_str() + " All queries finished, test concluded")
    if args.file is None:
        print("Final results for each request (as JSON): ")
        print(json.dumps(results, indent=4))
        print("To save results directly to a file, use the --file argument")
    else:
        json.dump(results, open(args.file, 'w'))
        print("Results saved to " + args.file)

# Handle command line arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default=None, type=str)
    args = parser.parse_args()
    main(args)