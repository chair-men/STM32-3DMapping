from read_write_dense import read_array
from read_write_model import read_model
import json
import cv2
import numpy as np
import pycolmap as cmap


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
    "/mnt/d/hochi/Desktop/heatmaps/lounge/colmap/dense/sparse")
image_ids = {image.name: [id, image.camera_id] for id, image in images.items()}


# Right Camera
right_image_name = "frame000106.png"
right_image_id, right_cam_id = image_ids[right_image_name]
camera_model = cameras[right_cam_id]
right_depth_map = read_array(
    f"/mnt/d/hochi/Desktop/heatmaps/lounge/colmap/dense/stereo/depth_maps/{right_image_name}.geometric.bin")
image_model = images[right_image_id]
right_cam_matrix = [
    -0.3052943092816547,
    0.01614754348082782,
    -0.9521211275671664,
    -1.0154003823305209,
    -0.9522580451824568,
    -0.005187694816518899,
    0.305250230479482,
    -0.4579557698788643,
    -0.000010272468978169205,
    0.9998561619863257,
    0.016960401895324977,
    -0.00612461213724888,
    0,
    0,
    0,
    1
]
right_cam_matrix = np.array(right_cam_matrix).reshape(4, 4)
camera_position = right_cam_matrix[:3, 3]
right_camera = cmap.Camera("OPENCV", camera_model.width, camera_model.height,
                           params=camera_model.params, id=camera_model.id)


def right_2d3d(poi):
    point2d = right_camera.image_to_world(poi) * right_depth_map[poi]
    x3d_cam = np.array(
        [point2d[0], point2d[1], -right_depth_map[poi]], dtype=np.float32)
    x_camera = np.append(x3d_cam, 1)
    x3d_world = (right_cam_matrix @ x_camera)[:3].reshape(3)
    return x3d_world


# Left Camera
left_image_name = "frame000137.png"
left_image_id, left_cam_id = image_ids[left_image_name]
camera_model = cameras[left_cam_id]
image_model = images[left_image_id]
left_depth_map = read_array(
    f"/mnt/d/hochi/Desktop/heatmaps/lounge/colmap/dense/stereo/depth_maps/{left_image_name}.geometric.bin")
left_cam_matrix = [
    -0.3122192493105115,
    0.14133212089475788,
    -0.9394383279190659,
    -0.644358342845607,
    -0.9500100738202626,
    -0.04644856923651136,
    0.3087448623959601,
    0.61716466213668,
    2.7755575615628907e-17,
    0.9888719644217198,
    0.14876907602297407,
    -0.09851932324860999,
    0,
    0,
    0,
    1
]
left_cam_matrix = np.array(left_cam_matrix).reshape(4, 4)
camera_position = left_cam_matrix[:3, 3]
left_camera = cmap.Camera("OPENCV", camera_model.width, camera_model.height,
                          params=camera_model.params, id=camera_model.id)


def left_2d3d(poi):
    point2d = left_camera.image_to_world(poi) * left_depth_map[poi]
    x3d_cam = np.array(
        [point2d[0], point2d[1], -left_depth_map[poi]], dtype=np.float32)
    x_camera = np.append(x3d_cam, 1)
    x3d_world = (left_cam_matrix @ x_camera)[:3].reshape(3)
    return x3d_world


with open("results.json", "r") as f:
    data = json.load(f)


final = []
for item in data.values():
    interm = []
    for _, annotation in item.items():
        id = annotation['id']
        cam_id = annotation['camera_id']
        x, y, width, height = annotation["bbox"]
        poi = (min(y + height, 1907), x + min(width // 2, 1073))
        if cam_id == 1:  # Left Camera
            convert_2d_to_3d = left_2d3d
        elif cam_id == 0:
            convert_2d_to_3d = right_2d3d
        x_3d = convert_2d_to_3d(poi)[:2]
        interm.append({id: list(x_3d)})
    final.append(interm)

with open('converted.json', 'w') as f:
    json.dump(final, f, indent=4)

box = [500, 800, 200, 200]
x, y, width, height = box
# poi = (y + height, x + (width // 2))
# print(poi)
poi = (560, 1000)
p3d = right_2d3d(poi)

annotate_image(
    "/mnt/d/hochi/Desktop/heatmaps/lounge/colmap/dense/images/frame000113.png", box)
