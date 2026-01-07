import csv
import itertools
import math
import os
from typing import List, Tuple
import matplotlib.pyplot as plt  # Added for visualization

os.chdir('C:/Users/geraint/Desktop/GitHub/tsm')

class OperationCounter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1

def haversine_distance(city1: Tuple[float, float], city2: Tuple[float, float], counter: OperationCounter) -> float:
    """Calculate Haversine distance between two cities (lat, lon in degrees) and count operation."""
    counter.increment()
    R = 6371  # Earth's radius in km
    lat1, lon1 = math.radians(city1[0]), math.radians(city1[1])
    lat2, lon2 = math.radians(city2[0]), math.radians(city2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def tsp_brute_force(cities: List[Tuple[float, float]], counter: OperationCounter) -> Tuple[float, List[int]]:
    n = len(cities)
    min_distance = float('inf')
    best_path = []
    
    for perm in itertools.permutations(range(1, n)):
        current_distance = haversine_distance(cities[0], cities[perm[0]], counter)
        for i in range(len(perm) - 1):
            current_distance += haversine_distance(cities[perm[i]], cities[perm[i+1]], counter)
        current_distance += haversine_distance(cities[perm[-1]], cities[0], counter)
        
        if current_distance < min_distance:
            min_distance = current_distance
            best_path = [0] + list(perm) + [0]
    
    return min_distance, best_path

def tsp_nearest_neighbor(cities: List[Tuple[float, float]], counter: OperationCounter) -> Tuple[float, List[int]]:
    n = len(cities)
    visited = [False] * n
    path = [0]
    visited[0] = True
    total_distance = 0.0
    
    current = 0
    for _ in range(n - 1):
        min_dist = float('inf')
        nearest = None
        for i in range(n):
            if not visited[i]:
                dist = haversine_distance(cities[current], cities[i], counter)
                if dist < min_dist:
                    min_dist = dist
                    nearest = i
        total_distance += min_dist
        path.append(nearest)
        visited[nearest] = True
        current = nearest
    
    total_distance += haversine_distance(cities[current], cities[0], counter)
    path.append(0)
    
    return total_distance, path

def measure_operations(func, cities: List[Tuple[float, float]]) -> Tuple[float, List[int], int]:
    counter = OperationCounter()
    distance, path = func(cities, counter)
    return distance, path, counter.count

def read_cities_from_csv(filename: str) -> List[Tuple[float, float]]:
    cities = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        header = next(reader, None)
        for row in reader:
            if len(row) >= 2:
                lat, lon = float(row[0]), float(row[1])
                cities.append((lat, lon))
    return cities

def save_route_to_csv(filename: str, cities: List[Tuple[float, float]], path: List[int], distance: float):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["City Index", "Latitude", "Longitude"])
        for idx in path:
            writer.writerow([idx, cities[idx][0], cities[idx][1]])
        writer.writerow(["Total Distance (km)", f"{distance:.4f}", ""])
    print(f"Route saved to '{filename}'")

def visualize_route(cities: List[Tuple[float, float]], path: List[int]):
    """Plot the TSM path using matplotlib."""
    lats = [cities[i][0] for i in path]
    lons = [cities[i][1] for i in path]
    
    plt.figure(figsize=(8, 6))
    plt.plot(lons, lats, 'o-', color='blue', markersize=8)
    for i, idx in enumerate(path):
        plt.text(lons[i], lats[i], str(idx), fontsize=9, color='red')
    plt.title("Traveling Salesman Route")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.show()

def main():
    input_file = input("Enter CSV file name with city coordinates (e.g., cities.csv): ").strip()
    try:
        cities = read_cities_from_csv(input_file)
        n = len(cities)
        print(f"Loaded {n} cities from {input_file}")
    except Exception:
        import random
        n = 10
        cities = [(random.uniform(-90, 90), random.uniform(-180, 180)) for _ in range(n)]
        print(f"Using {n} random cities for testing")
    
    if n > 15:
        current_function = tsp_nearest_neighbor
    else:
        current_function = tsp_brute_force
    
    distance, path, ops_count = measure_operations(current_function, cities)
    print(f"Distance: {distance:.4f} km, Path: {path}, Operations: {ops_count}")
    
    save_route_to_csv("tsm_route_output.csv", cities, path, distance)
    
    visualize = input("Would you like to visualize the route? (yes/no): ").strip().lower()
    if visualize == 'yes':
        visualize_route(cities, path)

if __name__ == "__main__":
    main()

