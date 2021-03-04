import pandas as pd
import os


class csv_processing:
    def __init__(self, input_path, output_path):
        self._input_path = input_path
        self._output_path = output_path
        filenames = os.listdir(input_path)
        filelist = []
        for file in filenames:
            if file.endswith('csv'):
                filelist.append(file)
        self._filelist = filelist

    def build_data(self):
        list1 = []
        filelist = self._filelist
        for i in filelist:
            path = os.path.join(self._input_path, i)
            data = pd.read_csv(path)
            list1.append(data)
        self._datalist = list1

    def save_excel(self):
        datas = self._datalist
        data = datas[0]
        for i in range(1, len(datas)):
            data = pd.merge(data, datas[i], how='inner', on='检查号')
        data.to_excel(os.path.join(self._output_path, 'csv转化excel文件.xlsx'))

    def save_csv(self):
        datas = self._datalist
        data = datas[0]
        for i in range(1, len(datas)):
            data = pd.merge(data, datas[i], how='inner', on='检查号')
        data.to_csv(os.path.join(self._output_path, 'csv转化文件.csv'))


if __name__ == '__main__':
    INPUT_PATH = r'C:\Users\SMIT\Desktop\data'
    OUTPUT_PATH = r'C:\Users\SMIT\Desktop\data'
    cte = csv_processing(INPUT_PATH, OUTPUT_PATH)
    cte.build_data()
    cte.save_excel()
    cte.save_csv()
