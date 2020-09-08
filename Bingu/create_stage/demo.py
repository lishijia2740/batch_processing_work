import numpy as np
import cv2

image = cv2.imread('test5.jpg', cv2.IMREAD_UNCHANGED)
edge = cv2.Canny(image, 200, 200)
print(edge)
edge = np.array(edge)
print(edge)
ans = []

height = image.shape[0]
width = image.shape[1]
# channels = image.shape[2]
# print("width : %s, height : %s channels : %s"%(width, height, channels))
for row in range(height):
    for col in range(width):
        if edge[row, col] != 0:
            ans = ans + [[col, row]]

print(ans)
cv2.imshow("pixels_demo", image)
cv2.waitKey(0)
# any = []
# for y in range(0, image.shape[1]):  # 宽
#     for x in range(0, image.shape[0]):  # 高
#         if image[x, y] != 0:
#             any = any + [[y, x]]
#
# right = any[-1]
# bottom = ans[-1]
# print(right)
# a = image.shape[0]  # 图片的高
# b = image.shape[1]  # 图片的宽
# print(a, b)
# sub4 = image[right[1]:, :]
#
# cv2.namedWindow("orient4", 0)  # 显示分割的子图2
# cv2.resizeWindow("orient4", 640, 480)
# cv2.imshow("orient4", sub4)
# cv2.imwrite('test5.jpg', sub4)
# cv2.waitKey(0)

# if __name__ == '__main__':
#     print(image.shape)
