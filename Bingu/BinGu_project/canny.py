import cv2 as cv

# 将图片进行边缘提取
def edge_demo(image):
    image = cv.imread(image)
    cv.namedWindow('title')
    cv.imshow('title', image)
    img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    canny_img_one = cv.Canny(img, 300, 150)
    canny_img_two = canny_img_one.copy()
    for i in range(0, canny_img_one.shape[0]):
        for j in range(0, canny_img_one.shape[1]):
            canny_img_two[i, j] = 255 - canny_img_one[i, j]
    cv.imshow('edge', canny_img_two)
    cv.imwrite('test3.jpg', canny_img_two)
    cv.waitKey(0)


edge_demo('test2.jpg')
