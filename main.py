import cv2
import numpy as np
import os
import pandas as pd
import re

def sort_filenames(filenames):
    sorted_filenames = sorted(filenames, key=lambda x: int(re.search(r'\d+', x).group()))
    return sorted_filenames

result = pd.DataFrame(columns=['Image', 'Total Area', 'Damaged Area', 'Damage Percentage'])
folder = 'tobacco-images'
files = os.listdir(folder)
image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png','.JPG'))]
images = sort_filenames(image_files)
for image_file in images:

    image = cv2.imread(os.path.join(folder, image_file))
    if image.shape[0] > 3500:
        input_image = cv2.resize(image, (int(image.shape[1] / 8), int(image.shape[0] / 8)))
    else:
        input_image = cv2.resize(image, (int(image.shape[1] / 5), int(image.shape[0] / 5)))

    final_contour_img = input_image.copy()
    contours_img = input_image.copy()
    result_image = input_image.copy()
    canny_result = input_image.copy()
    copy_img = input_image.copy()

    gray_scale_img = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('1.Gray Scale Image', gray_scale_img)
    #cv2.waitKey(0)

    gaussian_blur_img = cv2.GaussianBlur(gray_scale_img, (5, 5), 0)
    cv2.imshow('2.Image after Gaussian Blur Operation', gaussian_blur_img)
    #cv2.waitKey(0)

    canny = cv2.Canny(gaussian_blur_img, 20, 100)

    kernel = np.ones((3,3), np.uint8)

    dilated_edges = cv2.dilate(canny, kernel, iterations=1)
    cv2.imshow('3. Output after Dilating edges', dilated_edges)
    #cv2.waitKey(0)

    contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hull = [cv2.convexHull(cnt) for cnt in contours]

    smoothed_hull = []
    for h in hull:
        epsilon = 0.02 * cv2.arcLength(h, True)
        approx_hull = cv2.approxPolyDP(h, epsilon, True)
        smoothed_hull.append(approx_hull)

    combined_contours = np.zeros_like(gray_scale_img)

    cv2.drawContours(combined_contours, contours, -1, 255, 1)
    cv2.imshow('4.Contours after Canny Edge Detection', combined_contours)
    #cv2.waitKey(0)

    cv2.drawContours(combined_contours, smoothed_hull, -1, 255, 1)
    cv2.imshow('5.Contours after  Convex Hull', combined_contours)
    #cv2.waitKey(0)

    closed_combined = cv2.morphologyEx(combined_contours, cv2.MORPH_CLOSE, kernel)
    cv2.imshow('6.Combined contours after morphology operation', closed_combined)
    #cv2.waitKey(0)

    final_contours, _ = cv2.findContours(closed_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    maxval = 0
    id = 0
    for i in range(len(final_contours)):
        if len(final_contours[i]) > maxval:
            maxval = len(final_contours[i])
            id = i

    total_area = cv2.contourArea(final_contours[id])

    cv2.drawContours(final_contour_img,final_contours,-1,(0,0,255), 1)
    cv2.imshow('7.External Contour', final_contour_img)
    #cv2.waitKey(0)

    #for i in range(len(final_contours)):
    #   cv2.drawContours(contours_img,final_contours[i],-1,(0,0,255),3)
    #   print(cv2.contourArea(final_contours[i]))
    #   cv2.imshow('8.Individual Contour',contours_img)
    #   cv2.waitKey(0)

    cv2.drawContours(result_image, final_contours, -1, (0, 255, 0), 2)
    cv2.imshow('9.External/Outer contour', result_image)
    #cv2.waitKey(0)

    img = result_image

    gaussian_blur = cv2.GaussianBlur(img, (7,7), 1)
    cv2.imshow('10.Gaussian Blur', gaussian_blur)
    #cv2.waitKey(0)

    new_image = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    mean_shift_image = cv2.pyrMeanShiftFiltering(gaussian_blur, 20, 30, new_image, 0, criteria)
    cv2.imshow('11.Means Shift Image', mean_shift_image)
    #cv2.waitKey(0)

    result_edges = cv2.Canny(mean_shift_image, 297, 300)
    cv2.imshow('12.Result Edges', result_edges)
    #cv2.waitKey(0)

    kernel = np.ones((5, 5), np.uint8)
    closed_edges = cv2.morphologyEx(result_edges, cv2.MORPH_CLOSE, kernel)
    cv2.imshow('13.Closed Edges', closed_edges)
    #cv2.waitKey(0)

    contours, hierarchy = cv2.findContours(closed_edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    maxval = 0
    id = 0
    for i in range(len(contours)):
        if len(contours[i]) > maxval:
            maxval = len(contours[i])
            id = i

    #cv2.drawContours(canny_result, contours[id], -1, (255, 255, 255), 2)
    cv2.imshow('14.Large Contour', canny_result)
    #cv2.waitKey(0)

    damaged_area = 0
    loss = 0
    for i in range(len(contours)):
        if i == id:
            continue
        cv2.drawContours(canny_result,contours[i],-1,(0,0,255))
        if cv2.contourArea(contours[i]) > 10 and (cv2.contourArea(contours[i]) <= (total_area)/2):
            damaged_area += cv2.contourArea(contours[i])
        cv2.imshow('15.Final Contour',canny_result)
        #cv2.waitKey(0)

    loss = (damaged_area / total_area) * 100

    result_df = pd.DataFrame([{
        'Image': image_file,
        'Total Area': total_area,
        'Damaged Area': damaged_area,
        'Damage Percentage': loss
    }])
    cv2.waitKey(0)
    result = pd.concat([result, result_df], ignore_index=True)

    #print(f'Total Area of External Boundary: {total_area}')

result.to_excel('leaf_damage_analysis.xlsx', index=False)


