import numpy as np
import matplotlib.pyplot as plt

# 随便造的数据
x = np.array([1, 2, 3, 4, 5, 6, 7, 8])
y = np.array([1, 3, 7, 13, 26, 68, 150, 300])


# 计算参数函数-times为阶数
def cal(x, y, times):
    t = np.ones((times + 1, 8))
    for i in range(times):
        t[i + 1] = np.power(x, i + 1)

    x = t.T
    # 带入公式
    theta = np.linalg.inv((x.T.dot(x) + 0.001)).dot(x.T).dot(y)
    return theta


# 根据参数计算y值的函数-times为阶数
def getY(theta, x, times):
    t = np.ones((1, len(x)))
    for i in range(times + 1):
        t += np.power(x, i) * theta[i]

    return t

# 先把点画出来
plt.scatter(x, y)

a = np.linspace(1, 8, 100)

# 每别拟合1~7阶
for i in range(7):
    theta = cal(x, y, i + 1)
    # print(theta);
    b = getY(theta, a, i + 1)
    plt.plot(a, b.reshape(100))

labels = np.arange(1, 8, 1)
plt.legend(labels)
plt.show()
