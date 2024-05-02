import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import fiona
fiona.drvsupport.supported_drivers['ESRI Shapefile'] = 'rw'
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import Point
import matplotlib.lines as mlines
import numpy as np
import pulp
import shapely
import warnings
from mclp import mclp, plot_result
warnings.filterwarnings("ignore", message="Set SHAPE_RESTORE_SHX config option to YES")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
   
# Set the file paths for the shapefiles
streets_path = "/Users/ddani/Documents/konkuk.Univ./streets.shp"
client_points_path = "/Users/ddani/Documents/konkuk.Univ./client_points.shp"
bus_points_path = "/Users/ddani/Documents/konkuk.Univ./bus_points.shp"
cctv_path = "/Users/ddani/Documents/konkuk.Univ./cctv.shp"
cross_points_path = "/Users/ddani/Documents/konkuk.Univ./cross_points.shp"
commercial_points_path = "/Users/ddani/Documents/konkuk.Univ./commercial_points.shp"
facility_points_path = "/Users/ddani/Documents/konkuk.Univ./facility_points.shp"

# Read the shapefiles and convert them to GeoDataFrame
streets = gpd.read_file(streets_path)
client_points = gpd.read_file(client_points_path)
'''bus_points = gpd.read_file(bus_points_path)
cctv = gpd.read_file(cctv_path)
cross_points = gpd.read_file(cross_points_path)
commercial_points = gpd.read_file(commercial_points_path)'''
facility_points = gpd.read_file(facility_points_path)


# Set the parameters for analysis
CLIENT_COUNT = 100
FACILITY_COUNT = 10
SERVICE_RADIUS = 4

# Snapping function
def snap_points_to_network(points, network):
    snapped_points = []
    for point in points.geometry:
        nearest_line = None
        min_distance = float("inf")
        for line in network.geometry.dropna():
            if line.type == 'LineString':
                if line.intersects(point):
                    distance = line.distance(point)
                    if distance < min_distance:
                        nearest_line = line
                        min_distance = distance
        if nearest_line is not None:
            snapped_points.append(nearest_line.interpolate(nearest_line.project(point)))
        else:
            snapped_points.append(Point(point.x, point.y))
    return gpd.GeoDataFrame(geometry=snapped_points, crs=points.crs)

# Snap client points to the street network
streets_buffered = streets.buffer(0.5)
clients_snapped = snap_points_to_network(client_points, streets_buffered)

# Calculate weights for each client point based on proximity to other points
weights = np.zeros(len(clients_snapped))
'''proximity_points = [bus_points, cctv, cross_points, commercial_points]

for point_data in proximity_points:
    for point in point_data.geometry:
        indices = clients_snapped.geometry.distance(point) <= SERVICE_RADIUS
        weights[indices] += 1
'''
# Assign the calculated weights to the client points
clients_snapped["weights"] = weights

# Snap client points to the street network
streets_buffered = streets.buffer(0.5)
clients_snapped = snap_points_to_network(client_points, streets_buffered)

# Run mclp: opt_sites is the location of optimal sites and f is the points covered
opt_sites, f = mclp(clients_snapped.geometry, FACILITY_COUNT, SERVICE_RADIUS, len(client_points))

# Plot the points
fig, ax = plt.subplots(figsize=(10, 10))
streets.plot(ax=ax, alpha=0.8)
facility_points.plot(ax=ax, color="red", markersize=100, label="Facility Points")
clients_snapped.plot(
    ax=ax,
    color="blue",
    markersize=clients_snapped["weights"] * 10,
    label="Client Points",
)
plt.legend()
plt.show()
