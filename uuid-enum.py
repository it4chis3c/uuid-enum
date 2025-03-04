import uuid
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

def generate_uuids(mode, count):
    """Generate UUIDs based on the selected mode."""
    uuids = []
    if mode == "sequential":
        base_uuid = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        for i in range(count):
            new_uuid = uuid.UUID(int=base_uuid.int + i)
            uuids.append(str(new_uuid))
    elif mode == "random":
        uuids = [str(uuid.uuid4()) for _ in range(count)]
    return uuids

def check_uuid(target_url, uuid_value, timeout):
    """Send request with UUID and analyze the response."""
    url = target_url.replace("UUID_HERE", uuid_value)
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"[+] Valid UUID found: {uuid_value} (Status: 200, Length: {len(response.content)})")
            return uuid_value
        elif response.status_code in [403, 404]:
            print(f"[-] Invalid UUID: {uuid_value} (Status: {response.status_code})")
    except requests.RequestException as e:
        print(f"[!] Request error for UUID {uuid_value}: {e}")
    return None

def enumerate_uuids(target_url, mode, count, threads, timeout):
    """Enumerate UUIDs using multiple threads."""
    uuids = generate_uuids(mode, count)
    valid_uuids = []
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = executor.map(lambda u: check_uuid(target_url, u, timeout), uuids)
        valid_uuids = [r for r in results if r is not None]
    
    print("\nEnumeration complete. Valid UUIDs:")
    for valid in valid_uuids:
        print(valid)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UUID Enumeration Script")
    parser.add_argument("-u", "--url", required=True, help="Target URL with UUID_HERE placeholder")
    parser.add_argument("-m", "--mode", choices=["sequential", "random"], default="sequential", help="UUID generation mode")
    parser.add_argument("-c", "--count", type=int, default=100, help="Number of UUIDs to test")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of concurrent threads")
    parser.add_argument("-o", "--timeout", type=int, default=5, help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    enumerate_uuids(args.url, args.mode, args.count, args.threads, args.timeout)
