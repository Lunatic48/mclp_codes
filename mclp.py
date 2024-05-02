import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import fiona
fiona.drvsupport.supported_drivers['ESRI Shapefile'] = 'rw'
import geopandas as gpd
'''
from geopandas.io import file as io_file
io_file.fiona.drvsupport.supported_drivers['ESRI Shapefile'] = 'rw'
io_file.fiona.drvsupport.supported_drivers['ESRI Shapefile + SHX'] = 'rw'
'''
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import Point
import matplotlib.lines as mlines
import numpy as np
import pulp
import shapely

import warnings
warnings.filterwarnings("ignore", message="Set SHAPE_RESTORE_SHX config option to YES")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    #ignore deprecation warning - GH pysal/spaghetti#649
    #import spaghetti

# quantity demand points
CLIENT_COUNT = 100

# quantity supply points
FACILITY_COUNT = 10

# maximum service radius (in distance units)
SERVICE_RADIUS = 4

# number of candidate facilities in optimal solution
P_FACILITIES = 4

# random seeds for reproducibility
CLIENT_SEED = 5
FACILITY_SEED = 6

# set the solver
solver = pulp.COIN_CMD(msg=False, warmStart=True)

# Generate streets or use existing data
#streets 데이터 넣어주기
# Modify this part according to your data source and format
streets = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./streets.shp")
#about all points of client data
client_points = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./client_points.shp")
#for weight. 
bus_points = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./bus_points.shp")
cctv = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./cctv.shp")
cross_points = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./cross_points.shp")
commercial_points = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./commercial_points.shp")
facility_points = gpd.read_file("/Users/ddani/Documents/konkuk.Univ./facility_points.shp")

# Snapping function
def snap_points_to_network(points, network):
    snapped_points = []
    for point in points.geometry:
        nearest_line = network.geometry.interpolate(network.geometry.project(point))
        snapped_point = nearest_line.interpolate(nearest_line.project(point))
        snapped_points.append(snapped_point)
    return gpd.GeoDataFrame(geometry=snapped_points, crs=points.crs)

streets_buffered = gpd.GeoDataFrame(
    gpd.GeoSeries(streets["geometry"].buffer(0.5).unary_union),
    crs=streets.crs,
    columns=["geometry"],
)


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

#
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


matching_points1 = bus_points[bus_points.intersects(client_points.unary_union)]
matching_points2 = cctv[cctv.intersects(client_points.unary_union)]
matching_points3 = cross_points[cross_points.intersects(client_points.unary_union)]
matching_points4 = commercial_points[commercial_points.intersects(client_points.unary_union)]
matching_len=[len(matching_points1),len(matching_points2),len(matching_points3),len(matching_points4)]
print(matching_points1)

fig, ax = plt.subplots(figsize=(6, 6))

#weight(가중치 넣어주기))
np.random.seed(0)
#나중에는 random이 아니라 직접 넣어줘야 함.
ai = [0] * CLIENT_COUNT
'''
matching_points = [matching_points1, matching_points2, matching_points3, matching_points4]
weights = [5, 7, 9, 11]

for i, matching_points_i in enumerate(matching_points):
    for matching_point in matching_points_i.geometry:
        indices = client_points.geometry.intersects(matching_point)
        if indices.any():
            ai[indices] += weights[i]
'''
client_points["weights"] = ai
client_points["weights"].sum()

clients_snapped.plot(ax=ax, color="blue", label=f"clients sites ($n$={CLIENT_COUNT})")
facilities_snapped.plot(ax=ax, color="red", zorder=2, label=f"facility candidate sites ($n$={FACILITY_COUNT})")

# Plot streets
streets.plot(ax=ax, alpha=0.8, zorder=1, label="streets")

# Plot facility points
facility_points.plot(
    ax=ax, color="red", zorder=2, label=f"facility candidate sites ($n$={FACILITY_COUNT})"
)
#버전 2-weight
# 버전 2-weight
client_points.plot(
    ax=ax,
    color="black",
    label=f"clients sized weight\n\t$\sum$={client_points['weights'].sum()}",
    markersize=[ai[j]*2 for j in range(CLIENT_COUNT)]
)

#plot
plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
plt.grid(True)
plt.show()