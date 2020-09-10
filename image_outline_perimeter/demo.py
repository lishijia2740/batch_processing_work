# 局部阈值
# def local_threshold(image):
#     image = cv.imread(image)
#     gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)  # 把输入图像灰度化
#     # 自适应阈值化能够根据图像不同区域亮度分布，改变阈值
#     binary = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 25, 10)
#     cv.namedWindow("binary1", cv.WINDOW_NORMAL)
#     cv.imshow("binary1", binary)


# 用户自己计算阈值
# def custom_threshold(image):
#     image = cv.imread(image)
#     gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)  # 把输入图像灰度化
#     h, w = gray.shape[:2]
#     m = np.reshape(gray, [1, w * h])
#     mean = m.sum() / (w * h)
#     print("mean:", mean)
#     ret, binary = cv.threshold(gray, mean, 255, cv.THRESH_BINARY)
#     cv.namedWindow("binary2", cv.WINDOW_NORMAL)
#     cv.imshow("binary2", binary)
#     src = cv.imread('E:/imageload/kobe.jpg')
#     cv.namedWindow('input_image', cv.WINDOW_NORMAL)  # 设置为WINDOW_NORMAL可以任意缩放
#     cv.imshow('input_image', src)
#     threshold_demo(src)
#     local_threshold(src)
#     custom_threshold(src)
#     cv.waitKey(0)
#     cv.destroyAllWindow
