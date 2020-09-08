import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

bmi_life_data = pd.read_csv("bmi_and_life_expectancy.csv")
bmi_life_model = LinearRegression()
bmi_life_model.fit(bmi_life_data[['BMI']], bmi_life_data[['Life expectancy']])
laos_life_exp = bmi_life_model.predict([[21.07931]])
print(laos_life_exp)
ax = plt.scatter(bmi_life_data[['BMI']], bmi_life_data[['Life expectancy']])
plt.title('bmi_and_life_expectancy(LinearRegression)')
plt.xlabel("BMI")
plt.ylabel("Life expectancy")
print("coef_:", bmi_life_model.coef_)
print("intercept_:", bmi_life_model.intercept_)
x = np.linspace(18, 30, 1000)
y = bmi_life_model.coef_[0][0] * x + bmi_life_model.intercept_[0]
A = [0, bmi_life_model.intercept_[0]]
B = [-bmi_life_model.intercept_[0] / bmi_life_model.coef_[0][0], 0]
plt.plot(x, y, c='r')
