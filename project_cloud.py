import json
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

# Read point cloud from PLY file
ply_path = "./lounge/pcd/clean.ply"
# json_path = "./day3_left.json"
left_json_path = "results/day3_left.json"
right_json_path = "results/day3_right.json"
point_cloud = o3d.io.read_point_cloud(ply_path)

# Determine the rotation angle and axis
rotation_matrix = np.array(
    [
        [-0.01584073342382908, 0.20532387495040894, -0.9785658717155457],
        [0.99968421459198, -0.01584073342382908, -0.019506312906742096],
        [-0.019506312906742096, -0.9785658717155457, -0.20500808954238892],
    ]
)
point_cloud.rotate(rotation_matrix, center=point_cloud.get_center())

rotation_angle = np.pi / 9  # for a 30 degree rotation as an example
rotation_axis = np.array([0, 0, 1])

# Create the rotation matrix
rotation_matrix_2 = o3d.geometry.get_rotation_matrix_from_axis_angle(
    rotation_axis * rotation_angle
)

point_cloud.rotate(rotation_matrix_2, center=point_cloud.get_center())

# Rotate the point cloud

# with open(json_path, "r") as f:
#     annotations = json.load(f)
# f.close()

with open(left_json_path, "r") as f:
    left_annotations = json.load(f)
f.close()

with open(right_json_path, "r") as f:
    right_annotations = json.load(f)
f.close()

# print(annotations)
custom_points_left = []

custom_points_right = []

# Labels for custom points
labels = ["Camera 1", "Camera 0", "Point3D"]
center = point_cloud.get_center()
for annotation in left_annotations:
    for a in annotation:
        for idx, item in a.items():
            # if idx == "1":
            p = np.array(item)
            translated_p = p - center
            rotated_p_at_origin = rotation_matrix @ translated_p
            # rotated_p_at_origin = rotation_matrix_2 @ translated_p
            rotated_p = rotated_p_at_origin + center
            custom_points_left.append(rotated_p)
            labels.append("")
            # else:
            #     custom_points_2.append(item)
            #     labels.append("")

for annotation in right_annotations:
    for a in annotation:
        for idx, item in a.items():
            # if idx == "1":
            p = np.array(item)
            translated_p = p - center
            rotated_p_at_origin = rotation_matrix @ translated_p
            # rotated_p_at_origin = rotation_matrix_2 @ translated_p
            rotated_p = rotated_p_at_origin + center
            custom_points_right.append(rotated_p)
            labels.append("")
            # else:
            #     custom_points_2.append(item)
            #     labels.append("")

custom_points = np.array(custom_points_left)
custom_points = np.array(custom_points_right)

fig = plt.figure()
ax = fig.add_subplot()

ax.set_xlim([-7.5, 6])
ax.set_ylim([-5.5, 8.5])

ax.set_aspect("equal", adjustable="box")

# Plot and annotate each custom point
for i, point in enumerate(custom_points):
    ax.scatter(point[0], point[1], s=50, c="red", marker="x", label=labels[i])
# for i, point in enumerate(custom_points_2):
#     ax.scatter(point[0], point[1], point[2], s=50, c='blue', marker='x', label=labels[i])
# plt.annotate(labels[i], (point[0], point[1]), textcoords="offset points", xytext=(
#     0, 10), ha='center', fontsize=8, color='red')


# Voxel downsampling for making point cloud less dense
voxel_size = 0.4  # Define an appropriate voxel size
downsampled_point_cloud = point_cloud.voxel_down_sample(voxel_size)

# Extract points and colors as numpy arrays from downsampled point cloud
points = np.asarray(downsampled_point_cloud.points)
colors = np.asarray(downsampled_point_cloud.colors)

# Ensure colors are in a valid range for matplotlib [0, 1]
if colors.max() > 1:
    colors = colors / 255.0

# Project points to 2D (ignoring Z-coordinate for top-down perspective)
projected_points = points[:, :3]

# Visualize original points
ax.scatter(projected_points[:, 0], projected_points[:, 1], s=5, c=colors)

plt.show()


width = 654
height = 668

minx = -7.5
maxx = 6

miny = -5.5
maxy = 8.5

print(len(custom_points_left), len(custom_points_right))

for annotation in left_annotations:
    for a in annotation:
        for idx, item in a.items():
            p = np.array(item)
            translated_p = p - center
            rotated_p_at_origin = rotation_matrix @ translated_p
            rotated_p = rotated_p_at_origin + center
            rotated_p = rotated_p.tolist()
            rotated_p[0] = int(
                max(min(width - 1, ((rotated_p[0] - minx) * width) // (maxx - minx)), 0)
            )
            rotated_p[1] = int(
                max(
                    min(height - 1, ((rotated_p[1] - miny) * width) // (maxy - miny)), 0
                )
            )
            a[idx] = rotated_p[:2]

for annotation in right_annotations:
    for a in annotation:
        for idx, item in a.items():
            p = np.array(item)
            translated_p = p - center
            rotated_p_at_origin = rotation_matrix @ translated_p
            rotated_p = rotated_p_at_origin + center
            rotated_p = rotated_p.tolist()
            rotated_p[0] = int(
                max(min(width - 1, ((rotated_p[0] - minx) * width) // (maxx - minx)), 0)
            )
            rotated_p[1] = int(
                max(
                    min(height - 1, ((rotated_p[1] - miny) * width) // (maxy - miny)), 0
                )
            )
            a[idx] = rotated_p[:2]

with open("results/day3_image_left.json", "w") as f:
    json.dump(left_annotations, f)
f.close()

with open("results/day3_image_right.json", "w") as f:
    json.dump(right_annotations, f)
f.close()

print(len(left_annotations), len(right_annotations))
