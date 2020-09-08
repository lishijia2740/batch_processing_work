import numpy as np
import matplotlib.pyplot as plt
import cv2
import math
from sklearn.linear_model import LinearRegression, SGDRegressor
import pandas as pd

img = cv2.imread('test5.jpg')
edge = cv2.Canny(img, 200, 200)

ans = []
for y in range(0, edge.shape[0]):  # 高
    for x in range(0, edge.shape[1]):  # 宽
        if edge[y, x] != 0:
            ans = ans + [[x, y]]

any = []
for y in range(0, edge.shape[1]):  # 宽
    for x in range(0, edge.shape[0]):  # 高
        if edge[x, y] != 0:
            any = any + [[y, x]]

for i in range(len(any) - 1):
    if any[i + 1][0] == any[i][0]:
        any[i] = 0
while True:
    any.remove(0)
    if 0 not in any:
        break

x_scatter = []
y_scatter = []
for i in any:
    x_scatter.append(i[0])
    y_scatter.append(-i[1])

plt.scatter(x=x_scatter, y=y_scatter, c='red', marker="*")
plt.show()

left = any[0]
right = any[-1]
bottom = ans[-1]

botton_index = any.index(ans[-1])

a_lines = any[:botton_index]
b_lines = any[botton_index:]

# print(a_lines)
# print(b_lines)

demo = []
for i in a_lines:
    demo.append(i[0])
    demo.append(i[1])
data = np.array(demo)
a = data.size // 2
new = data.reshape(a, 2)
new_list = list(new)

demo1 = []
for i in b_lines:
    demo1.append(i[0])
    demo1.append(i[1])

data1 = np.array(demo1)
a1 = data1.size // 2
new1 = data1.reshape(a1, 2)
new_list1 = list(new1)

name = ['x', 'y']
test_list = [left, bottom]
test_list2 = [bottom, right]
print(type(new_list1))
test = pd.DataFrame(columns=name, data=new_list)
test1 = pd.DataFrame(columns=name, data=new_list1)

test_list = pd.DataFrame(columns=name, data=test_list)

test_list2 = pd.DataFrame(columns=name, data=test_list2)

print(new_list)
print(new_list1)
print(test)
print(test1)

# 使用其中的一个feature
# diabetes_X = test.loc[:, 'x']
# diabetes_X = list(diabetes_X)
# diabetes_X = np.array(diabetes_X).reshape(-1, 1)
# print(diabetes_X)

right_x_train = test1.loc[:, 'x']
right_x_train = np.array(right_x_train).reshape(-1, 1)

# 将数据集分割成training set和test set
# diabetes_X_train = diabetes_X
# diabetes_X_test = diabetes_X[-20:]
#
# test_x = test_list.loc[:, 'x']
# test_x = np.array(test_x).reshape(-1, 1)

test_x1 = test_list2.loc[:, 'x']
test_x1 = np.array(test_x1).reshape(-1, 1)

# diabetes_X_test = test_x
# 将目标（y值）分割成training set和test set
# target_y = test.loc[:, 'y']
# # target_y = list(target_y)
# target_y = np.array(target_y).reshape(-1, 1)
# # print((target_y))

right_y_train = test1.loc[:, 'y']
right_y_train = np.array(right_y_train).reshape(-1, 1)

# diabetes_y_train = target_y

test_y = -test_list.loc[:, 'y']
test_y = np.array(test_y).reshape(-1, 1)
# diabetes_y_test = diabetes_y_train[-20:]


# 使用线性回归
regr = LinearRegression()
regr1 = LinearRegression()

# 进行training set和test set的fit，即是训练的过程
# regr.fit(diabetes_X_train, -diabetes_y_train)
regr1.fit(right_x_train, -right_y_train)

# y2 = regr.predict(test_x)
y3 = regr1.predict(test_x1)

print(y3.coef_)
print(y3.intercapton)

# left = [left[0], y2[0]]
#
# bottom = [bottom[0], y2[1]]
# bottom1 = [bottom[0], y3[0]]
# right = [right[0], y3[1]]

# plt.plot(diabetes_y_test, y2, 'g-')
# plt.show()
# 打印出相关系数和截距等信息
# print('Coefficients: \n', regr.coef_)
# # The mean square error
# print("Residual sum of squares: %.2f"
#       % np.mean((regr.predict(diabetes_X_test) - diabetes_y_test) ** 2))
# # Explained variance score: 1 is perfect prediction
# print('Variance score: %.2f' % regr.score(diabetes_X_test, diabetes_y_test))
#
# # 使用pyplot画图
# plt.scatter(right_x_train, -right_y_train, color='black')
# plt.plot(test_list2, y3, color='blue', linewidth=3)

# print(test_x1)
# print(y3)

# plt.show()

a_line = left + bottom
b_line = right + bottom


# 计算角度
# def angle(v1, v2):
#     dx1 = v1[2] - v1[0]
#     dy1 = v1[3] - v1[1]
#     dx2 = v2[2] - v2[0]
#     dy2 = v2[3] - v2[1]
#     angle1 = math.atan2(dy1, dx1)
#     angle1 = int(angle1 * 180 / math.pi)
#     # print(angle1)
#     angle2 = math.atan2(dy2, dx2)
#     angle2 = int(angle2 * 180 / math.pi)
#     # print(angle2)
#     if angle1 * angle2 >= 0:
#         included_angle = abs(angle1 - angle2)
#     else:
#         included_angle = abs(angle1) + abs(angle2)
#         if included_angle > 180:
#             included_angle = 360 - included_angle
#     return included_angle
#
#
# ang1 = angle(a_line, b_line)
# print(ang1)

