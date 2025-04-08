#!/bin/bash
# test_scenarios.sh - Run various network disruption scenarios

# Scenario 1: High Latency on Worker 1
echo "Running Scenario 1: High Latency on Worker 1 (200ms)"
python3 network_sim.py --proxy worker1_proxy --latency 200 --duration 60

# Wait for system to recover
sleep 10

# Scenario 2: Packet Loss on Worker 2
echo "Running Scenario 2: Packet Loss on Worker 2 (5%)"
python3 network_sim.py --proxy worker2_proxy --loss 5.0 --duration 60

# Wait for system to recover
sleep 10

# Scenario 3: Limited Bandwidth on Worker 3
echo "Running Scenario 3: Limited Bandwidth on Worker 3 (1Mbit/s)"
python3 network_sim.py --proxy worker3_proxy --bandwidth 1000 --duration 60

# Wait for system to recover
sleep 10

# Scenario 4: High Latency on All Workers
echo "Running Scenario 4: High Latency and Jitter on All Workers"
python3 network_sim.py --proxy worker1_proxy --latency 100 --jitter 50 &
python3 network_sim.py --proxy worker2_proxy --latency 100 --jitter 50 &
python3 network_sim.py --proxy worker3_proxy --latency 100 --jitter 50 &
sleep 60

# Clear all conditions
python3 network_sim.py --proxy worker1_proxy --clear
python3 network_sim.py --proxy worker2_proxy --clear
python3 network_sim.py --proxy worker3_proxy --clear

# Wait for system to recover
sleep 10

# Scenario 5: Complete Outage of Worker 1
echo "Running Scenario 5: Complete Outage of Worker 1"
python3 network_sim.py --proxy worker1_proxy --disable
sleep 60
python3 network_sim.py --proxy worker1_proxy --enable

echo "All test scenarios completed"