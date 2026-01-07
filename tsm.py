import csv
import itertools
import math
import os
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.animation as animation

os.chdir('C:/Users/geraint/Desktop/GitHub/tsm')

class OperationCounter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1

def haversine_distance(city1: Tuple[float, float], city2: Tuple[float, float], counter: OperationCounter) -> float:
    counter.increment()
    R = 6371
    lat1, lon1 = math.radians(city1[0]), math.radians(city1[1])
    lat2, lon2 = math.radians(city2[0]), math.radians(city2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def tsp_nearest_neighbor_2opt(cities: List[Tuple[float, float]], counter: OperationCounter, max_iterations: int = 50) -> Tuple[float, List[int], List[List[int]]]:
    """Nearest neighbor + 2-opt with path history for animation."""
    n = len(cities)
    visited = [False] * n
    path = [0]
    visited[0] = True
    total_distance = 0.0
    
    # Nearest neighbor phase
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
    
    # Store history for animation
    path_history = [path.copy()]
    
    # 2-opt improvement
    improved = True
    iteration = 0
    while improved and iteration < max_iterations:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                old_dist = (haversine_distance(cities[path[i-1]], cities[path[i]], counter) +
                            haversine_distance(cities[path[j]], cities[path[j+1]], counter))
                new_dist = (haversine_distance(cities[path[i-1]], cities[path[j]], counter) +
                            haversine_distance(cities[path[i]], cities[path[j+1]], counter))
                if new_dist < old_dist:
                    path[i:j+1] = path[i:j+1][::-1]
                    total_distance += new_dist - old_dist
                    improved = True
        iteration += 1
        path_history.append(path.copy())  # store every iteration
    
    return total_distance, path, path_history

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

def animate_route(cities: List[Tuple[float, float]], path_history: List[List[int]]):
    fig, ax = plt.subplots(figsize=(8,6))
    
    lats = [c[0] for c in cities]
    lons = [c[1] for c in cities]
    
    scat = ax.plot([], [], 'o-', color='blue', markersize=8)[0]
    
    for i, idx in enumerate(range(len(cities))):
        ax.text(lons[i], lats[i], str(i), fontsize=9, color='red')
    
    ax.set_xlim(min(lons)-1, max(lons)+1)
    ax.set_ylim(min(lats)-1, max(lats)+1)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("TSM Route Optimization (Nearest Neighbor + 2-Opt)")
    ax.grid(True)
    
    def update(frame):
        current_path = path_history[frame]
        x = [cities[i][1] for i in current_path]
        y = [cities[i][0] for i in current_path]
        scat.set_data(x, y)
        return scat,
    
    ani = animation.FuncAnimation(fig, update, frames=len(path_history), interval=500, blit=True, repeat=False)
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
    
    counter = OperationCounter()
    distance, path, path_history = tsp_nearest_neighbor_2opt(cities, counter)
    print(f"Final Distance: {distance:.4f} km, Path: {path}, Operations: {counter.count}")
    
    save_route_to_csv("tsm_route_output.csv", cities, path, distance)
    
    visualize = input("Visualize the optimization process? (yes/no): ").strip().lower()
    if visualize == 'yes':
        animate_route(cities, path_history)

if __name__ == "__main__":
    main()
