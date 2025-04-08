#!/usr/bin/env python3
"""
Network simulation script for Docker containers using ToxiProxy
"""

import argparse
import requests
import json
import time
import sys

TOXIPROXY_URL = "http://localhost:8474"

def list_proxies():
    """List all available proxies"""
    response = requests.get(f"{TOXIPROXY_URL}/proxies")
    if response.status_code == 200:
        proxies = response.json()
        print("Available proxies:")
        for name, proxy in proxies.items():
            print(f"  - {name}: {proxy['listen']} → {proxy['upstream']}")
    else:
        print(f"Error: Unable to list proxies. Status code: {response.status_code}")

def add_latency(proxy_name, latency, jitter=0):
    """Add latency to a proxy"""
    toxic = {
        "name": "latency",
        "type": "latency",
        "stream": "downstream",
        "toxicity": 1.0,
        "attributes": {
            "latency": latency,
            "jitter": jitter
        }
    }
    
    response = requests.post(
        f"{TOXIPROXY_URL}/proxies/{proxy_name}/toxics",
        json=toxic
    )
    
    if response.status_code == 200:
        print(f"Added {latency}ms latency (jitter: {jitter}ms) to {proxy_name}")
    else:
        print(f"Error: Unable to add latency to {proxy_name}. Status code: {response.status_code}")
        print(response.text)

def add_packet_loss(proxy_name, percent):
    """Add packet loss to a proxy"""
    toxic = {
        "name": "loss",
        "type": "timeout",
        "stream": "downstream",
        "toxicity": percent / 100.0,
        "attributes": {
            "timeout": 100
        }
    }
    
    response = requests.post(
        f"{TOXIPROXY_URL}/proxies/{proxy_name}/toxics",
        json=toxic
    )
    
    if response.status_code == 200:
        print(f"Added {percent}% packet loss to {proxy_name}")
    else:
        print(f"Error: Unable to add packet loss to {proxy_name}. Status code: {response.status_code}")
        print(response.text)

def add_bandwidth_limit(proxy_name, rate_kbps):
    """Add bandwidth limitation to a proxy"""
    toxic = {
        "name": "bandwidth",
        "type": "bandwidth",
        "stream": "downstream",
        "toxicity": 1.0,
        "attributes": {
            "rate": rate_kbps
        }
    }
    
    response = requests.post(
        f"{TOXIPROXY_URL}/proxies/{proxy_name}/toxics",
        json=toxic
    )
    
    if response.status_code == 200:
        print(f"Limited bandwidth to {rate_kbps}kbps on {proxy_name}")
    else:
        print(f"Error: Unable to limit bandwidth on {proxy_name}. Status code: {response.status_code}")
        print(response.text)

def clear_toxics(proxy_name):
    """Remove all toxics from a proxy"""
    response = requests.get(f"{TOXIPROXY_URL}/proxies/{proxy_name}/toxics")
    if response.status_code != 200:
        print(f"Error: Unable to get toxics for {proxy_name}. Status code: {response.status_code}")
        return False
    
    toxics = response.json()
    for toxic in toxics:
        toxic_name = toxic["name"]
        delete_response = requests.delete(
            f"{TOXIPROXY_URL}/proxies/{proxy_name}/toxics/{toxic_name}"
        )
        if delete_response.status_code == 204:
            print(f"Removed toxic '{toxic_name}' from {proxy_name}")
        else:
            print(f"Error: Failed to remove toxic '{toxic_name}' from {proxy_name}")
    
    return True

def disable_proxy(proxy_name):
    """Disable a proxy (simulate complete outage)"""
    response = requests.post(
        f"{TOXIPROXY_URL}/proxies/{proxy_name}",
        json={"enabled": False}
    )
    
    if response.status_code == 200:
        print(f"Disabled proxy {proxy_name} (simulating complete outage)")
    else:
        print(f"Error: Unable to disable {proxy_name}. Status code: {response.status_code}")
        print(response.text)

def enable_proxy(proxy_name):
    """Enable a previously disabled proxy"""
    response = requests.post(
        f"{TOXIPROXY_URL}/proxies/{proxy_name}",
        json={"enabled": True}
    )
    
    if response.status_code == 200:
        print(f"Enabled proxy {proxy_name}")
    else:
        print(f"Error: Unable to enable {proxy_name}. Status code: {response.status_code}")
        print(response.text)

def main():
    parser = argparse.ArgumentParser(description="Network simulation for Docker containers")
    
    # General options
    parser.add_argument("--list", action="store_true", help="List available proxies")
    parser.add_argument("--proxy", type=str, help="Proxy name to modify")
    parser.add_argument("--duration", type=int, help="Duration in seconds for the toxic condition")
    parser.add_argument("--clear", action="store_true", help="Clear all toxics from the proxy")
    
    # Network conditions
    parser.add_argument("--latency", type=int, help="Add latency in milliseconds")
    parser.add_argument("--jitter", type=int, help="Add jitter in milliseconds (requires --latency)")
    parser.add_argument("--loss", type=float, help="Add packet loss percentage (0-100)")
    parser.add_argument("--bandwidth", type=int, help="Limit bandwidth in kbps")
    parser.add_argument("--disable", action="store_true", help="Disable the proxy (complete outage)")
    parser.add_argument("--enable", action="store_true", help="Enable a disabled proxy")
    
    args = parser.parse_args()
    
    if args.list:
        list_proxies()
        return
    
    if not args.proxy:
        if not args.list:
            print("Error: --proxy is required unless using --list")
        return
    
    if args.clear:
        clear_toxics(args.proxy)
        return
    
    if args.disable:
        disable_proxy(args.proxy)
        return
    
    if args.enable:
        enable_proxy(args.proxy)
        return
    
    # Apply the specified conditions
    if args.latency:
        add_latency(args.proxy, args.latency, args.jitter or 0)
    
    if args.loss:
        if args.loss < 0 or args.loss > 100:
            print("Error: Loss percentage must be between 0 and 100")
            return
        add_packet_loss(args.proxy, args.loss)
    
    if args.bandwidth:
        add_bandwidth_limit(args.proxy, args.bandwidth)
    
    # Wait for the specified duration if provided
    if args.duration:
        print(f"Condition will be active for {args.duration} seconds")
        try:
            time.sleep(args.duration)
            print("Duration complete, clearing conditions")
            clear_toxics(args.proxy)
        except KeyboardInterrupt:
            print("\nInterrupted, clearing conditions")
            clear_toxics(args.proxy)

if __name__ == "__main__":
    main()