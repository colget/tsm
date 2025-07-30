import csv
import itertools
import math
import os
from typing import List, Tuple

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
    """Brute-force TSM: try all permutations."""
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
    """Nearest neighbor heuristic for TSM with 2-opt improvement."""
    n = len(cities)
    visited = [False] * n
    path = [0]  # Start at city 0
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
    
    # 2-opt improvement phase (limited iterations for efficiency)
    improved = True
    max_iterations = 50
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
    
    return total_distance, path

def measure_operations(func, cities: List[Tuple[float, float]]) -> Tuple[float, List[int], int]:
    """Measure operations for a TSM function."""
    counter = OperationCounter()
    distance, path = func(cities, counter)
    return distance, path, counter.count

def read_cities_from_csv(filename: str) -> List[Tuple[float, float]]:
    """Read city coordinates (latitude, longitude) from a CSV file."""
    cities = []
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            header = next(reader, None)  # Skip header if present
            for row in reader:
                if len(row) >= 2:
                    lat, lon = float(row[0]), float(row[1])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        cities.append((lat, lon))
                    else:
                        raise ValueError(f"Invalid coordinates: {row}")
        if not 2 <= len(cities) <= 100:
            raise ValueError("Number of cities must be between 2 and 100.")
        return cities
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        raise
    except (ValueError, IndexError) as e:
        print(f"Error: Invalid data in CSV file. {str(e)}")
        raise

def save_route_to_csv(filename: str, cities: List[Tuple[float, float]], path: List[int], distance: float):
    """Save the route and distance to a CSV file."""
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["City Index", "Latitude", "Longitude"])
            for idx in path:
                writer.writerow([idx, cities[idx][0], cities[idx][1]])
            writer.writerow(["Total Distance (km)", f"{distance:.4f}", ""])
        print(f"Route saved to '{filename}'")
    except IOError:
        print(f"Error: Could not write to '{filename}'")

def main():
    # Get input file
    input_file = input("Enter CSV file name with city coordinates (e.g., cities.csv): ").strip()
    try:
        cities = read_cities_from_csv(input_file)
        n = len(cities)
        print(f"Loaded {n} cities from {input_file}")
    except Exception:
        print("Falling back to random cities due to input error.")
        while True:
            try:
                n = int(input("Enter number of cities (2 to 100): ") or 20)
                if 2 <= n <= 100:
                    break
                print("Please enter a number between 2 and 100.")
            except ValueError:
                print("Please enter a valid integer.")
        import random
        random.seed(42)
        cities = [(random.uniform(-90, 90), random.uniform(-180, 180)) for _ in range(n)]
    
    iteration = 0
    current_function = tsp_brute_force
    current_ops = float('inf')
    efficiency_improved = False
    
    print(f"Testing TSM for {n} cities in global logistics")
    
    while True:
        iteration += 1
        print(f"Iteration {iteration}: Testing compute efficiency")
        
        # Skip brute-force for large n to prevent excessive computation
        if n > 15 and current_function == tsp_brute_force:
            print(f"Skipping brute-force for n={n} (too computationally expensive)")
            distance, path, ops_count = float('inf'), [], float('inf')
        else:
            distance, path, ops_count = measure_operations(current_function, cities)
            print(f"Distance: {distance:.4f} km, Path: {path}, Operations: {ops_count}")
        
        # Try the alternative function if not already improved
        if not efficiency_improved:
            next_function = tsp_nearest_neighbor if current_function == tsp_brute_force else tsp_brute_force
            next_distance, next_path, next_ops_count = measure_operations(next_function, cities)
            print(f"Alternative function operations: {next_ops_count}, Distance: {next_distance:.4f} km")
            
            # Check if the alternative uses fewer operations
            if next_ops_count < ops_count or (n > 15 and next_function == tsp_nearest_neighbor):
                print(f"Efficiency improvement detected: {ops_count} ops -> {next_ops_count} ops")
                current_function = next_function
                current_ops = next_ops_count
                efficiency_improved = True
                print("Efficiency improved (fewer operations), exiting loop to continue execution...")
                break
            else:
                print("No efficiency improvement detected, continuing loop...")
        
        # Safety break to prevent infinite loop
        if iteration > 10:
            print("Safety break: Maximum iterations reached")
            break
    
    # Continue with optimized function and save results
    if efficiency_improved:
        print("Program continuing with optimized TSM function for global logistics")
        distance, path, final_ops = measure_operations(current_function, cities)
        print(f"Final calculation: Distance = {distance:.4f} km, Path = {path}, Operations = {final_ops}")
        
        # Save route to output file
        output_file = "tsm_route_output.csv"
        save_route_to_csv(output_file, cities, path, distance)
        
        # Offer visualization
        visualize = input("Would you like to visualize the route? (yes/no): ").strip().lower()
        if visualize == 'yes':
            print("Visualization would be generated here (e.g., matplotlib or Folium plot).")
            # Note: Visualization code omitted per guidelines unless confirmed
    else:
        print("Program continuing without optimization")

if __name__ == "__main__":
    main()