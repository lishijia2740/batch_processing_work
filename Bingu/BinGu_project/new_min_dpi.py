import cv2

image = cv2.imread('test3.jpg', cv2.IMREAD_COLOR)

edge = cv2.Canny(image, 200, 200)

ans = []
for y in range(0, edge.shape[0]):  # 高
    for x in range(0, edge.shape[1]):  # 宽
        if edge[y, x] != 0:
            ans = ans + [[y, x]]

any = []
for y in range(0, edge.shape[1]):  # 宽
    for x in range(0, edge.shape[0]):  # 高
        if edge[x, y] != 0:
            any = any + [[x, y]]
print(ans)
print(any)

right = any[-1]
bottom = ans[-1]
# print(right)
a = image.shape[0]  # 图片的高
b = image.shape[1]  # 图片的宽
# print(a,b)

sub4 = image[right[0]:, :]

cv2.namedWindow("orient4", 0)  # 显示分割的子图2
cv2.resizeWindow("orient4", 640, 480)
cv2.imshow("orient4", sub4)
cv2.imwrite('test5.jpg', sub4)
cv2.waitKey(0)
