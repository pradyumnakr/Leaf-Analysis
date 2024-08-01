import os
import cv2
import numpy as np
import pandas as pd

def process_images(folder, result_file):
    df = pd.DataFrame(columns=['Image', 'Total Area', 'Damaged Area', 'Damage Percentage'])

    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png','.JPG'))]
    for image_file in image_files:
        old = cv2.imread(os.path.join(folder, image_file))
        img = cv2.resize(old, (int(old.shape[1] / 5), int(old.shape[0] / 5)))

        #cv2.imshow('Original Image', old)
        #cv2.imshow('Resized Image', img)
        img_cop = img.copy()

        gaussion_blur = cv2.GaussianBlur(img, (7, 7), 1)
        #cv2.imshow('Gaussian Blur', gaussion_blur)

        new_image = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

        mean_shift = cv2.pyrMeanShiftFiltering(gaussion_blur, 20, 30, new_image, 0, criteria)
        #cv2.imshow('Means Shift Image', mean_shift)

        edged = cv2.Canny(gaussion_blur, 130, 200)
        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        #cv2.imshow('Canny Edges After Contouring', edged)
        print("Number of Contours found = " + str(len(contours)))

        maxval = 0
        id = 0
        for i in range(len(contours)):
            if len(contours[i]) > maxval:
                maxval = len(contours[i])
                id = i

        #cv2.drawContours(img_cop,contours[id],-1,(255,255,255), 2)
        #cv2.imshow(' Large Contour', img_cop)
        #cv2.waitKey(0)

        total_area = cv2.contourArea(contours[id])
        print("The total area of the leaf is: " + str(total_area))

        #for i in range(len(contours)):
        #    cv2.drawContours(img,contours[i],-1,(0,0,255))
        #    print(cv2.contourArea(contours[i]))
        #    cv2.imshow('Contour',img)
        #    cv2.waitKey(0)

        cv2.drawContours(img_cop, contours, -1, (0, 255, 0), 1)
        #cv2.imshow('Contours', img_cop)

        canny = cv2.cvtColor(edged,cv2.COLOR_GRAY2BGR)
        height, width, _ = canny.shape
        min_x, min_y = width, height
        max_x = max_y = 0

        for contour, hier in zip(contours, hierarchy):
            (x, y, w, h) = cv2.boundingRect(contours[id])
            min_x, max_x = min(x, min_x), max(x + w, max_x)
            min_y, max_y = min(y, min_y), max(y + h, max_y)
            if w > 80 and h > 80:
                roi = img[y:y + h, x:x + w]
                originalroi = img[y:y + h, x:x + w]

        if (max_x - min_x > 0 and max_y - min_y > 0):
            roi = img[min_y:max_y, min_x:max_x]
            originalroi = img[min_y:max_y, min_x:max_x]

        img1 = roi

        hls_image = cv2.cvtColor(img1, cv2.COLOR_BGR2HLS)
        #cv2.imshow('HLS', hls_image)

        hue_channel = hls_image[:,:,0]
        #cv2.imshow('img_hue hls',hue_channel)

        ret, thresh = cv2.threshold(hue_channel,60,255,cv2.THRESH_BINARY_INV)
        #cv2.imshow('thresh', thresh)

        mask = cv2.bitwise_and(originalroi,originalroi,mask = thresh)
        #cv2.imshow('masked out img',mask)

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hullimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _, img_gray = cv2.threshold(img_gray,150,255,cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(img_gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        hull_list= []
        defect_list= []
        for i in range(len(contours)):
            hull = cv2.convexHull(contours[i], returnPoints= False)
            hull[::-1].sort(axis=0)
            defects = cv2.convexityDefects(contours[i],hull)
            hull = cv2.convexHull(contours[i])
            hull_list.append(hull)
            defect_list.append(defects)

        for idx, defects in enumerate(defect_list):
            #cv2.drawContours(img, hull_list, idx, (255,0,0),2)
            if defects is None:
                continue
            for i in range(defects.shape[0]):
                s,e,_,d = defects[i,0]
                if d > 8000:
                    start = tuple(contours[idx][s][0])
                    end = tuple(contours[idx][e][0])
                    cv2.line(hullimg,start,end,[0,255,0],1)

        #cv2.imshow('img',hullimg)

        contours, heirarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        damaged_area = 0

        #cv2.imshow("original",originalroi)
        for x in range(len(contours)):
            cv2.drawContours(originalroi, contours[x], -1, (0, 0, 255))
            #cv2.imshow('Contour masked', originalroi)
            #cv2.waitKey(0)

            damaged_area += cv2.contourArea(contours[x])
            #print(cv2.contourArea(contours[x]))

        loss = (damaged_area/total_area) * 100

        print("Total area of the leaf: ", total_area)
        print("Total damaged area: ",damaged_area)
        print("The percentage of damaged area: ", loss)

        result_df = pd.DataFrame([{
            'Image': image_file,
            'Total Area': total_area,
            'Damaged Area': damaged_area,
            'Damage Percentage': loss
        }])

        df = pd.concat([df, result_df], ignore_index=True)

        #cv2.waitKey(0)

    #cv2.destroyAllWindows()
    #with pd.ExcelWriter('leaf_damage_analysis.xlsx', engine='openpyxl') as writer:
    #    df.to_excel(writer, index=False)
    df.to_excel(result_file, index=False)