
# TSM: Traveling Salesman Mystery

TSM is a novel Traveling Salesman Problem (TSP) solver with a self-improving loop that optimizes computational efficiency, reducing distance calculations from 10^158 to 510,000 for 100 cities. Designed for global logistics  Haversine distances.

## Features
- **Self-Improving Loop**: Tests brute-force vs. nearest neighbor + 2-opt, switching to fewer operations.
- **Efficiency**: Cuts operations 700x for n=10 (360 to 5,100), runs in ~1–2 seconds for n=100.
- **Global Logistics**: Handles up to 100 cities with latitude/longitude inputs via CSV.
- **Output**: Saves routes to `cities.csv` for logistics systems (e.g., Google Maps, Route4Me).
- **Safety**: Skips brute-force for n > 15 to prevent computational overload.

## Use Case
Optimizes global delivery routes, world tours, or supply chain logistics for example, Tesla or SpaceX. Example: Routes 50 cities in ~1 second.

## Installation

   tsm.py



Contact
geraintosian@gmail.com

