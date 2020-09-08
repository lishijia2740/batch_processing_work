import pandas as pd
import numpy as np

pd.set_option('expand_frame_repr', False)  # 数据超过总宽度后，是否折叠显示
pd.set_option('max_colwidth', 100)  # 设置单列的宽度，用字符个数表示，单个数据长度超出该数时以省略号表示
pd.set_option('show_dimensions', True)  # 当数据带省略号显示时，是否在最后显示数据的维度


class VisveraAbnormal:
    def __init__(self, input_file):
        self._file = input_file

    def get_sheet(self):
        """
        获取excel文件所有sheet
        :return:
        """
        sheet_name_list = []
        file = pd.ExcelFile(self._file)
        for i in file.sheet_names[0:5]:
            sheet_name_list.append(i)
        return sheet_name_list

    def build_dataframe(self, sheetname):
        """
        将excel中每个sheet的数据都遍历执行，构建dataframe
        :return:
        """
        all_data = pd.read_excel(self._file, header=1, sheetname=sheetname)
        # 构建新的列，用来备注异常位置
        all_data.loc[:, 'abnormal'] = ''
        all_data.loc[:, 'visvera'] = sheetname
        radial_line_x = all_data.loc[:, ['A号', 'NoC', 'AP', 'PVP', 'DP-early', 'DP-item', 'DP-late', 'abnormal']]
        radial_line_y = all_data.loc[:,
                        ['A号', 'NoC.1', 'AP.1', 'PVP.1', 'DP-early.1', 'DP-item.1', 'DP-late.1', 'abnormal']]
        radial_line_z = all_data.loc[:,
                        ['A号', 'NoC.2', 'AP.2', 'PVP.2', 'DP-early.2', 'DP-item.2', 'DP-late.2', 'abnormal']]
        volume = all_data.loc[:,
                 ['A号', 'NoC.3', 'AP.3', 'PVP.3', 'DP-early.3', 'DP-item.3', 'DP-late.3', 'abnormal']]
        ct_avg = all_data.loc[:,
                 ['A号', 'NoC.4', 'AP.4', 'PVP.4', 'DP-early.4', 'DP-item.4', 'DP-late.4', 'abnormal']]
        radial_line_x.loc[:, 'pos'] = "径线X"
        radial_line_y.loc[:, 'pos'] = "径线Y"
        radial_line_z.loc[:, 'pos'] = "径线Z"
        volume.loc[:, 'pos'] = "体积"
        ct_avg.loc[:, 'pos'] = "CT平均值"
        self._all_data = all_data
        datas = [radial_line_x, radial_line_y, radial_line_z, volume, ct_avg]
        return datas

    def abnormal_precessing(self, data):
        """
        将abnormal列中，拼接数字替换，不影响查看
        :return:
        """
        for i in range(len(data.index)):
            for j in ['.1', '.2', '.3', '.4']:
                data.iloc[i] = data.iloc[i].replace(j, '')
        return data

    def col_analyze(self, datas, n):
        """
        列方向分析异常值，返回结果存入abnormal
        :param radial_line_x:   构建的DataFrame

        A号        NoC         AP        PVP   DP-early    DP-item
0    A002905253  30.242556  39.965484        NaN        NaN  32.333421
1    A002926846  43.164668  43.310709        NaN  46.294548        NaN
2    A002930574  43.922559  42.768043        NaN  44.396025        NaN
3    A002934149  45.331145  37.447831  21.212967        NaN        NaN
4    A002934153  43.985022  40.447139        NaN  33.659616        NaN


        :return:    添加 pos和abnormal后的DataFrame

       A号        NoC         AP        PVP   DP-early     DP-item         DP-late       pos       abnormal
0    A002905253  30.242556  39.965484        NaN        NaN  32.333421       NaN       径线X      径线X_DP-early,
1    A002926846  43.164668  43.310709        NaN  46.294548        NaN       NaN       径线X      径线X_PVP,
2    A002930574  43.922559  42.768043        NaN  44.396025        NaN       NaN       径线X      径线X_NoC,
3    A002934149  45.331145  37.447831  21.212967        NaN        NaN       NaN       径线X      径线X_NoC,
4    A002934153  43.985022  40.447139        NaN  33.659616        NaN       NaN       径线X      径线X_AP,径线X_NoC,径线X_DP-early,
        """
        # 列方向
        datas = datas[:-1]
        for data in datas:
            # 异常值检测3sigma原则
            # n = 1.5  # n*sigma
            # 均值：np.mean（arr，0）
            # 标准差：np.std(arr, 0)
            demo = data.index
            # print(demo)
            outlier_inedx = []  # 异常值索引
            for i in range(len(demo)):
                demo = data.iloc[i, 1:-2]
                print(demo)
                ymean = np.mean(demo)
                ystd = np.std(demo)
                floor = ymean - n * ystd
                upper = ymean + n * ystd
                #
                y = demo
                for j in range(len(y)):
                    print(y[j])
                    if (y[j] < floor) | (y[j] > upper):
                        # if not in
                        self._all_data.loc[i, 'abnormal'] = self._all_data.loc[i, 'abnormal'] + self._all_data.loc[
                            i, 'visvera'] + '_' + data.loc[i, 'pos'] + '_' + data.columns[j + 1] + ','
                        outlier_inedx.append(j + 1)
                    else:
                        continue
        self._all_data.loc[:, 'abnormal'] = self.abnormal_precessing(self._all_data.loc[:, 'abnormal'])
        print(self._all_data.loc[:, ['A号', 'abnormal']])
        return

    def row_analyze(self, datas, n):
        # 行方向
        # datas = self.build_dataframe()
        for data in datas:
            # 获取NoC
            for j in data.columns[1:-2]:
                current_column = data.loc[:, j]
                ymean = np.mean(current_column)
                ystd = np.std(current_column)
                floor = ymean - n * ystd
                upper = ymean + n * ystd
                #
                y = current_column
                for i in range(0, len(y)):
                    if (y[i] < floor) | (y[i] > upper):
                        self._all_data.loc[i, 'abnormal'] = self._all_data.loc[i, 'abnormal'] + self._all_data.loc[
                            i, 'visvera'] + '_' + data.loc[i, 'pos'] + '_' + j + ','
                    else:
                        continue
        self._all_data.loc[:, 'abnormal'] = self.abnormal_precessing(self._all_data.loc[:, 'abnormal'])
        return self._all_data

    def mjm(self, n):
        """
        门静脉特殊处理
        :return:
        """
        mjm_data = pd.read_excel(self._file, header=1, sheetname='门静脉')
        pjm = mjm_data.iloc[:, 1:6]
        mjm = mjm_data.iloc[:, 6:11]
        cxmsjm = mjm_data.iloc[:, 11:16]
        pjm.loc[:, 'pos'] = '脾静脉-label__1008-86'
        mjm.loc[:, 'pos'] = '门静脉-label__1208'
        cxmsjm.loc[:, 'pos'] = '肠系膜上静脉-label__1212'
        mjm_data.loc[:, 'abnormal'] = ''
        datas = [pjm, mjm, cxmsjm]
        for data in datas:
            # 获取NoC
            for j in data.columns[:-2]:
                current_column = data.loc[:, j]
                ymean = np.mean(current_column)
                ystd = np.std(current_column)
                floor = ymean - n * ystd
                upper = ymean + n * ystd
                y = current_column
                for i in range(0, len(y)):
                    if (y[i] < floor) | (y[i] > upper):
                        mjm_data.loc[i, 'abnormal'] = mjm_data.loc[i, 'abnormal'] + '门静脉' + '_' + data.loc[
                            i, 'pos'] + '_' + j + ','
                    else:
                        continue
        mjm_data.loc[:, 'abnormal'] = self.abnormal_precessing(mjm_data.loc[:, 'abnormal'])
        print(mjm_data.loc[:, ['A号', 'abnormal']])
        return mjm_data


if __name__ == '__main__':
    # n * sigma，设置倍数
    N = 1
    INPUT_FILE = '腹部脏器统计_20200823.xlsx'
    va = VisveraAbnormal(INPUT_FILE)
    sheetnames = va.get_sheet()
    for i in sheetnames:
        data = va.build_dataframe(i)
        va.row_analyze(data, N)
        va.col_analyze(data, N)
    va.mjm(N)
