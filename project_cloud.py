import json
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

# Read point cloud from PLY file
ply_path = './lounge/pcd/clean.ply'
json_path = './converted.json'
point_cloud = o3d.io.read_point_cloud(ply_path)

# Determine the rotation angle and axis
rotation_angle = np.pi / 9  # for a 30 degree rotation as an example
rotation_axis = np.array([0, 0, 1])

# Create the rotation matrix
rotation_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle(
    rotation_axis * rotation_angle)
# point_cloud.rotate(rotation_matrix, center=point_cloud.get_center())

# Rotate the point cloud

with open(json_path, "r") as f:
    annotations = json.load(f)

custom_points = np.array([
    [-0.64435834,  0.61716466],
    [-1.01540038, -0.45795577],
    [0.54544966, -1.00447661]
])

# Labels for custom points
labels = ['Camera 1', 'Camera 0', "Point3D"]

# Plot and annotate each custom point
for i, point in enumerate(custom_points):
    plt.scatter(point[0], point[1], s=50, c='red', marker='x', label=labels[i])
    plt.annotate(labels[i], (point[0], point[1]), textcoords="offset points", xytext=(
        0, 10), ha='center', fontsize=8, color='red')


# Voxel downsampling for making point cloud less dense
voxel_size = 0.005  # Define an appropriate voxel size
downsampled_point_cloud = point_cloud.voxel_down_sample(voxel_size)

# Extract points and colors as numpy arrays from downsampled point cloud
points = np.asarray(downsampled_point_cloud.points)
colors = np.asarray(downsampled_point_cloud.colors)

# Ensure colors are in a valid range for matplotlib [0, 1]
if colors.max() > 1:
    colors = colors / 255.0

# Project points to 2D (ignoring Z-coordinate for top-down perspective)
projected_points = points[:, :2]

# Visualize original points
plt.scatter(projected_points[:, 0], projected_points[:, 1], s=5, c=colors)

plt.show()
