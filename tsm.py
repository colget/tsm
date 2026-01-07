import csv
import math
import matplotlib.pyplot as plt
from typing import List, Tuple
import random

# ---------------------------
# Distance Functions
# ---------------------------

def haversine_distance(city1: Tuple[float,float], city2: Tuple[float,float]) -> float:
    """Haversine distance in km."""
    R = 6371
    lat1, lon1 = math.radians(city1[0]), math.radians(city1[1])
    lat2, lon2 = math.radians(city2[0]), math.radians(city2[1])
    dlat, dlon = lat2-lat1, lon2-lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

def compute_distance_matrix(cities: List[Tuple[float,float]]) -> List[List[float]]:
    n = len(cities)
    dist = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = haversine_distance(cities[i], cities[j])
            dist[i][j] = dist[j][i] = d
    return dist

# ---------------------------
# Nearest Neighbor + 2-opt
# ---------------------------

def nearest_neighbor_tour(start_idx: int, dist: List[List[float]]) -> List[int]:
    n = len(dist)
    visited = [False]*n
    tour = [start_idx]
    visited[start_idx] = True
    current = start_idx

    for _ in range(n-1):
        next_city = min((i for i in range(n) if not visited[i]),
                        key=lambda i: dist[current][i])
        tour.append(next_city)
        visited[next_city] = True
        current = next_city
    tour.append(start_idx)
    return tour

def two_opt(tour: List[int], dist: List[List[float]], max_iter=100) -> List[int]:
    n = len(tour)
    improved = True
    it = 0
    while improved and it < max_iter:
        improved = False
        for i in range(1,n-2):
            for j in range(i+1,n-1):
                a,b = tour[i-1], tour[i]
                c,d = tour[j], tour[j+1]
                if dist[a][b] + dist[c][d] > dist[a][c] + dist[b][d]:
                    tour[i:j+1] = reversed(tour[i:j+1])
                    improved = True
        it += 1
    return tour

def tour_distance(tour: List[int], dist: List[List[float]]) -> float:
    return sum(dist[tour[i]][tour[i+1]] for i in range(len(tour)-1))

# ---------------------------
# Virtual Circle Clustering
# ---------------------------

def circle_clusters(cities: List[Tuple[float,float]], radius_factor=1.0) -> List[List[int]]:
    n = len(cities)
    clusters = []
    assigned = set()
    
    # Create all pair midpoints and half-distances
    pairs = []
    for i in range(n):
        for j in range(i+1,n):
            midpoint = ((cities[i][0]+cities[j][0])/2, (cities[i][1]+cities[j][1])/2)
            radius = haversine_distance(cities[i], cities[j])*0.5*radius_factor
            pairs.append((midpoint, radius, (i,j)))
    
    # Sort pairs by radius descending
    pairs.sort(key=lambda x: x[1], reverse=True)
    
    for center, r, (i,j) in pairs:
        if i in assigned and j in assigned:
            continue
        # Find all cities within this circle
        cluster = [k for k in range(n) if haversine_distance(cities[k], center) <= r]
        # Skip if already assigned
        cluster = [k for k in cluster if k not in assigned]
        if cluster:
            clusters.append(cluster)
            assigned.update(cluster)
    # Assign any remaining cities individually
    for k in range(n):
        if k not in assigned:
            clusters.append([k])
            assigned.add(k)
    return clusters

# ---------------------------
# CSV and Visualization
# ---------------------------

def read_cities_from_csv(filename: str) -> List[Tuple[float,float]]:
    cities = []
    with open(filename,'r') as f:
        reader = csv.reader(f)
        header = next(reader,None)
        for row in reader:
            if len(row)>=2:
                cities.append((float(row[0]), float(row[1])))
    return cities

def visualize_clusters(cities: List[Tuple[float,float]], clusters: List[List[int]], hub_idx=0):
    colors = plt.cm.get_cmap('tab20', len(clusters))
    plt.figure(figsize=(10,8))
    for idx, cluster in enumerate(clusters):
        lats = [cities[i][0] for i in cluster]
        lons = [cities[i][1] for i in cluster]
        plt.scatter(lons, lats, color=colors(idx), label=f'Cluster {idx+1}')
        plt.scatter(cities[hub_idx][1], cities[hub_idx][0], color='black', s=100, label='Hub' if idx==0 else "")
    plt.title("Delivery Clusters")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True)
    plt.show()

# ---------------------------
# Main Program
# ---------------------------

def main():
    input_file = "delivery_points.csv"
    hub_idx = 0  # First city is the warehouse/hub
    cities = read_cities_from_csv(input_file)
    print(f"Loaded {len(cities)} delivery points")
    
    dist_matrix = compute_distance_matrix(cities)
    
    # Cluster cities into zones for vehicles
    clusters = circle_clusters(cities, radius_factor=1.0)
    print(f"Generated {len(clusters)} clusters for vehicles")
    
    visualize_clusters(cities, clusters, hub_idx=hub_idx)
    
    # Solve TSP for each cluster
    for v, cluster in enumerate(clusters):
        # Include hub in cluster
        cluster_with_hub = [hub_idx] + [c for c in cluster if c != hub_idx]
        submatrix = [[dist_matrix[i][j] for j in cluster_with_hub] for i in cluster_with_hub]
        tour = nearest_neighbor_tour(0, submatrix)
        tour = two_opt(tour, submatrix)
        distance = tour_distance(tour, submatrix)
        tour_cities = [cluster_with_hub[i] for i in tour]
        print(f"Vehicle {v+1}: {len(cluster)} stops, Distance = {distance:.2f} km, Tour = {tour_cities}")

if __name__=="__main__":
    main()
