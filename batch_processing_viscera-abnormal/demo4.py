import pandas as pd

# df = pd.DataFrame([(.21, .32), (.01, .6), ('sdf', .03), (.21, .183)], columns=['dogs', 'cats'])
# print(df)
# for i in range(len(df.index)):
#     for j in df.columns:
#         df.loc[i, j] = '%.2f'%df.loc[i, j]
# print(df)
mean = 34.18
# list1 = [12, 3, 4]
# avestd = [(abs(i+mean+z))/list1.count z=i+meanfor i in list1]
# print(avestd)
# b = 0
# for i in list1:
#     b += abs(i+mean)
import math

# print(b/len(list1))
a = math.sqrt(((30.24 - mean) ** 2 + (39.97 - mean) ** 2 + (32.33 - mean) ** 2) / 3)
print(a)
