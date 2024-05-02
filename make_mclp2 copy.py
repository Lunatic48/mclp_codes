import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import fiona
fiona.drvsupport.supported_drivers['ESRI Shapefile'] = 'rw'
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import Point
from geopandas import GeoSeries  # 추가
from pandas import Series 
from mclp import *

import matplotlib.lines as mlines
import numpy as np
import pulp
import shapely
from shapely.geometry import LineString

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # ignore deprecation warning - GH pysal/spaghetti#649
    import spaghetti

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # ignore deprecation warning - GH pysal/libpysal#468
    lattice = spaghetti.regular_lattice((0, 0, 10, 10), 9, exterior=True)
ntw = spaghetti.Network(in_data=lattice)
   

# quantity demand points
CLIENT_COUNT = 100
FACILITY_COUNT = 10
SERVICE_RADIUS = 4

# number of candidate facilities in optimal solution
P_FACILITIES = 4

# random seeds for reproducibility
CLIENT_SEED = 5
FACILITY_SEED = 6

# set the solver
solver = pulp.COIN_CMD(msg=False, warmStart=True)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # ignore deprecation warning - GH pysal/libpysal#468
    lattice = spaghetti.regular_lattice((0, 0, 10, 10), 9, exterior=True)
ntw = spaghetti.Network(in_data=lattice)

#streets 데이터 넣어주기
#streets = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./streets.shp")
#about all points of client data
#client_points = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./client_points.shp")

streets = spaghetti.element_as_gdf(ntw, arcs=True)
streets_buffered = gpd.GeoDataFrame(
    gpd.GeoSeries(streets["geometry"].buffer(0.5).unary_union),
    crs=streets.crs,
    columns=["geometry"],
)

'''
def simulated_geo_points(streets_buffered, needed, seed):
    np.random.seed(seed)
    points = []
    while len(points) < needed:
        x = np.random.uniform(streets_buffered.bounds.minx, streets_buffered.bounds.maxx)
        y = np.random.uniform(streets_buffered.bounds.miny, streets_buffered.bounds.maxy)
        point = Point(x, y)
        if streets_buffered.contains(point).any():
            points.append(point)
    return gpd.GeoDataFrame(geometry=points, crs=streets_buffered.crs)

# Snapping function
def snap_points_to_network(points, network):
    snapped_points = []
    for point in points.geometry:
        nearest_line = network.geometry.interpolate(network.geometry.project(point))
        if nearest_line.is_empty:
            snapped_points.append(Point())  # None for unsnapped points
        else:
            snapped_point = nearest_line.interpolate(nearest_line.project(point))
            snapped_points.append(snapped_point)
    # Convert snapped_points to LineString
    snapped_lines = [LineString([p]) for p in snapped_points]
    
    return gpd.GeoDataFrame(geometry=snapped_lines, crs=points.crs)

client_points = simulated_geo_points(
    streets_buffered, needed=CLIENT_COUNT, seed=CLIENT_SEED
)
facility_points = simulated_geo_points(
    streets_buffered, needed=FACILITY_COUNT, seed=FACILITY_SEED
)
# Snap client points to the street network
clients_snapped = snap_points_to_network(client_points, streets_buffered)
clients_snapped = gpd.GeoDataFrame(geometry=clients_snapped.geometry, crs=client_points.crs)

# Snap facility points to the street network
facilities_snapped = snap_points_to_network(facility_points, streets_buffered)
facilities_snapped = gpd.GeoDataFrame(geometry=facilities_snapped.geometry, crs=facility_points.crs)


# Assign the calculated weights to the client points
weights = np.random.randint(1, 12, len(clients_snapped))
clients_snapped["weights"] = weights

fig, ax = plt.subplots(figsize=(10, 10))


#ai =client_points["weights"].tolist()

clients_snapped.plot(ax=ax, color="blue", label=f"clients sites ($n$={CLIENT_COUNT})")
facilities_snapped.plot(ax=ax, color="red", zorder=2, label=f"facility candidate sites ($n$={FACILITY_COUNT})")

# Plot streets
streets.plot(ax=ax, alpha=0.8, zorder=1, label="streets")

# Plot facility points
facility_points.plot(
    ax=ax, color="red", zorder=2, label=f"facility candidate sites ($n$={FACILITY_COUNT})"
)
#버전 2-weight

client_points.plot(
    ax=ax,
    color="black",
    label=f"clients sized weight\n\t$\sum$={client_points['weights'].sum()}",
    markersize=[ai[j]*2 for j in range(CLIENT_COUNT)]
)

# Get the top 100 client points based on weights
top_client_points = client_points.nlargest(100, "weights")

# Get the list of weights for the top 100 client points
ai = top_client_points["weights"].tolist()

fig, ax = plt.subplots(figsize=(6, 6))

# Plot streets
streets.plot(ax=ax, alpha=0.8, zorder=1, label="streets")

# Plot facility points
facility_points.plot(
    ax=ax, color="red", zorder=2, label=f"facility candidate sites ($n$={FACILITY_COUNT})"
)

# Plot top 100 client points with marker size based on weights
top_client_points.plot(
    ax=ax,
    color="black",
    label=f"top 100 clients based on weight",
    markersize=[ai[j]*2 for j in range(100)]
)

# Plot legend and grid
plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
plt.grid(True)

# Show the plot
plt.show()
'''