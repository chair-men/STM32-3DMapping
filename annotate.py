import json
import cv2
import numpy as np
import pycolmap as cmap
from read_write_dense import read_array
from read_write_model import read_model
from scipy.spatial.transform import Rotation as R


def get_image_tf(image_model):
    qvec = image_model.qvec
    rvec = R.from_quat([qvec[1], qvec[2], qvec[3], qvec[0]])
    tvec = image_model.tvec
    tf_matrix = np.row_stack(
        (
            np.column_stack((rvec.as_matrix(), tvec.reshape(3, 1))),
            np.array([[0, 0, 0, 1]]),
        )
    )
    return np.linalg.inv(tf_matrix)


def annotate_image(image_path, bounding_box):
    # Read the image
    image = cv2.imread(image_path)

    # Check if image is loaded successfully
    if image is None:
        print("Error: Unable to load image.")
        return

    # Draw the bounding box
    x, y, width, height = bounding_box
    cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), 2)

    # Display the image
    # cv2.namedWindow("Annotated Image", cv2.WINDOW_NORMAL)
    cv2.imwrite(f"{image_path}_annotated.png", image)

    # Wait for a key event and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()


cameras, images, points = read_model(
    "/mnt/d/hochi/Desktop/heatmaps/lounge/colmap/dense/sparse"
)
image_ids = {image.name: [id, image.camera_id] for id, image in images.items()}


# Right Camera
right_image_name = "frame000113.png"
right_depth_name = "frame000106.png"
right_image_id, right_cam_id = image_ids[right_image_name]
camera_model = cameras[right_cam_id]
image_model = images[right_image_id]
right_image_tf = get_image_tf(image_model)
right_depth_map = read_array(
    f"/mnt/d/hochi/Desktop/heatmaps/lounge/colmap/dense/stereo/depth_maps/{right_depth_name}.geometric.bin"
)
right_camera = cmap.Camera(
    "OPENCV",
    camera_model.width,
    camera_model.height,
    params=camera_model.params,
    id=camera_model.id,
)


def right_2d3d(poi):
    point2d = right_camera.image_to_world(poi) * right_depth_map[poi]
    x3d_cam = np.array([point2d[0], point2d[1], right_depth_map[poi]], dtype=np.float32)
    x_camera = np.append(x3d_cam, 1)
    x3d_world = (right_image_tf @ x_camera)[:3].reshape(3)
    return x3d_world


# Left Camera
left_image_name = "frame000143.png"
left_depth_name = "frame000137.png"
left_image_id, left_cam_id = image_ids[left_image_name]
camera_model = cameras[left_cam_id]
image_model = images[left_image_id]
left_image_tf = get_image_tf(image_model)
left_depth_map = read_array(
    f"/mnt/d/hochi/Desktop/heatmaps/lounge/colmap/dense/stereo/depth_maps/{left_depth_name}.geometric.bin"
)
left_camera = cmap.Camera(
    "OPENCV",
    camera_model.width,
    camera_model.height,
    params=camera_model.params,
    id=camera_model.id,
)


def left_2d3d(poi):
    point2d = left_camera.image_to_world(poi) * left_depth_map[poi]
    x3d_cam = np.array([point2d[0], point2d[1], left_depth_map[poi]], dtype=np.float32)
    x_camera = np.append(x3d_cam, 1)
    x3d_world = (left_image_tf @ x_camera)[:3].reshape(3)
    return x3d_world


with open("results.json", "r") as f:
    data = json.load(f)


final = []
for item in data.values():
    interm = []
    for _, annotation in item.items():
        id = annotation["id"]
        cam_id = annotation["camera_id"]
        x, y, width, height = annotation["bbox"]
        poi = (min(y + height, 1907), min(x + width // 2, 1073))
        if cam_id == 1:  # Left Camera
            convert_2d_to_3d = left_2d3d
        elif cam_id == 0:
            convert_2d_to_3d = right_2d3d
        x_3d = convert_2d_to_3d(poi)
        interm.append({id: list(x_3d)})
    final.append(interm)

with open("converted.json", "w") as f:
    json.dump(final, f, indent=4)
