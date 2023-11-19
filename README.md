# STM32-3DMapping

## Steps for reproduction:

1. Take a video of the location you wish to map out (without any people around)
2. Split the video into frames
3. Pass the individual frames through COLMAP (sparse) using COLMAP's GUI to generate sparse depth maps + camera poses
4. Use the camera poses and depth maps to generate a NeRF using nerfstudio
5. Establish the 3D pointcloud and estimated 3D positions of locations in the map from top down
6. Take other videos with people around, and split the video into frames
7. Estimate the camera poses of these videos with relation to the above provided camera poses
8. Pass the individual frames through MiDaS to get the arbitrary estimated depths of each pixel on the frames
9. Pass the individual frames through the multicamera tracking algorithm to get the 2D position on the frames
10. Compare the estimated depth of an area in the center of the bounding box with the depth as given by NeRF to get the estimated depth in the scale of NeRF
11. Using the camera poses generated, estimate the 3D position of the individual person with backprojection

## References used

- [COLMAP](https://github.com/colmap/colmap) to generate sparse reconstruction and get camera views
- [MiDaS](https://github.com/isl-org/MiDaS) to generate estimates of depths in real time
- [nerfstudio](https://github.com/nerfstudio-project/nerfstudio/) to generate dense pointcloud and get views


## Link to used assets

[OneDrive](https://entuedu-my.sharepoint.com/:f:/g/personal/c210142_e_ntu_edu_sg/EvkrtEfyySxHm9Dm8RCMUhkBwQXT0Fb-Sk__Y9CACh863w?e=nIkXfW)