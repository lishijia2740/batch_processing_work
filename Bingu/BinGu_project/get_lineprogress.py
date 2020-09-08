import numpy as np
import matplotlib.pyplot as plt
import cv2
from create_stage.atan2 import angle
from sklearn.linear_model import LinearRegression
import pandas as pd

img = cv2.imread('test5.jpg')
edge = cv2.Canny(img, 200, 200)
# 水平读取
ans = []
for y in range(0, edge.shape[0]):  # 高
    for x in range(0, edge.shape[1]):  # 宽
        if edge[y, x] != 0:
            ans = ans + [[x, y]]

# 竖直读取
any = []
for y in range(0, edge.shape[1]):  # 宽
    for x in range(0, edge.shape[0]):  # 高
        if edge[x, y] != 0:
            any = any + [[y, x]]

# 去重相同经度的坐标
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

bottom_index = any.index(ans[-1])

# 获取以bottom为界限的两列像素点
a_lines = any[:bottom_index]
b_lines = any[bottom_index:]


# 构建像素坐标列表
def get_lines(lines):
    demo1 = []
    for i in lines:
        demo1.append(i[0])
        demo1.append(i[1])
    data1 = np.array(demo1)
    a1 = data1.size // 2
    new1 = data1.reshape(a1, 2)
    new_list1 = list(new1)
    return new_list1


a_new_list = get_lines(a_lines)
b_new_list = get_lines(b_lines)

left = any[0]
right = any[-1]
bottom = ans[-1]

# 预测的相关节点
test_alist = [left, bottom]
test_blist = [bottom, right]


# 构建训练集
def build_data(list):
    name = ['x', 'y']
    data = pd.DataFrame(columns=name, data=list)
    data_feature = data.loc[:, 'x']
    data_target = data.loc[:, 'y']
    data_feature = np.array(data_feature).reshape(-1, 1)
    data_target = np.array(data_target).reshape(-1, 1)
    return data_feature, -data_target


a_data_feature, a_data_target = build_data(a_new_list)
b_data_feature, b_data_target = build_data(b_new_list)

test_alist, p_a = build_data(test_alist)
test_blist, p_b = build_data(test_blist)


# 构建线性回归
def Line_Regression(features, target):
    regr = LinearRegression()
    regr.fit(features, target)
    return regr


regr = Line_Regression(a_data_feature, a_data_target)
regr1 = Line_Regression(b_data_feature, b_data_target)

y1 = regr.predict(test_alist)
y2 = regr1.predict(test_blist)


def found_bottom(regr, regr1):
    a1 = float(regr.coef_)  # 系数
    b1 = float(regr.intercept_)  # 截距
    a2 = float(regr1.coef_)
    b2 = float(regr1.intercept_)
    # print(a1, b1, a2, b2)
    ff = a1 - a2
    if a1 - a2 < 0:
        ff = abs(a1 - a2)
    x = round(abs(b2 - b1) // ff)
    # x = np.array(x).reshape(-1, 1)
    y = round(float((a1 * x) + b1))
    return x, y


left = [left[0], int(y1[0])]
right = [right[0], int(y2[1])]

bottom_x, bottom_y = found_bottom(regr, regr1)
bottom = [bottom_x, bottom_y]

polt_x = [left[0], bottom_x, right[0]]
polt_y = [left[1], bottom_y, right[1]]

if __name__ == '__main__':
    plt.scatter(x=x_scatter, y=y_scatter, c='red', marker="*")
    plt.show()
    plt.scatter(a_data_feature, a_data_target, color='black')
    plt.plot(test_alist, y1, color='blue', linewidth=3)
    plt.show()
    plt.scatter(b_data_feature, b_data_target, color='black')
    plt.plot(test_blist, y2, color='blue', linewidth=3)
    plt.show()
    plt.plot(polt_x, polt_y, color='green')
    plt.show()
    a_line = left + bottom
    b_line = bottom + right

    print('髌骨夹角角度为:', angle(a_line, b_line))
