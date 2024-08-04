## Image Processing Steps

| Step | Description | Image |
|------|-------------|-------|
| 1 | Images are converted to gray scale to reduce complexity. | <img src="result/1.Gray-Scale.png" alt="Grayscale Image" width="300" height="300"> |
| 2 | Gaussian Blur operation applied on gray scale image to remove noise. | <img src="result/2.Gaussian-Blur.png" alt="Gaussian Blur" width="300" height="300"> |
| 3 | Dilated to make it more visible. | <img src="result/3.Dilation.png" alt="Dilation" width="300" height="300"> |
| 4 | Canny edge detection is applied to mark external boundary. | <img src="result/5.Canny.png" alt="Canny Edge Detection" width="300" height="300"> |
| 5 | Convex hull operation applied to approximate the shape of the leaf. | <img src="result/6.Convex-Hull.png" alt="Convex Hull" width="300" height="300"> |
| 6 | Approximate shape after combining the canny with convex hull algorithm. | <img src="result/9.Result.png" alt="Result" width="300" height="300"> |
| 7 | Application of Gaussian blur on the result image. | <img src="result/10.Gaussian-Blur.png" alt="Gaussian Blur on Result" width="300" height="300"> |
| 8 | Further removal of noise by mean shift algorithm. | <img src="result/11.Mean-Shift-Image.png" alt="Mean Shift Image" width="300" height="300"> |
| 9 | Apply canny edge detection to extract contours in the image. | <img src="result/12.Canny.png" alt="Canny Edge Detection" width="300" height="300"> |
| 10 | Close the contours if any in the image. | <img src="result/13.Closed-Edges.png" alt="Closed Edges" width="300" height="300"> |
| 11 | Final result with all the contours in the image. | <img src="result/14.Final.png" alt="Final Result" width="300" height="300"> |


