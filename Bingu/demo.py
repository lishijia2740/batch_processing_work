import os
import shutil


def eachFile(filepath, OUTPUT_PATH):
    fileNames = os.listdir(filepath)  # 获取当前路径下的文件名，返回List
    # print(fileNames)
    # file 文件名
    count = 1
    new_dir_list = []
    try:
        for file in fileNames:
            newDir = filepath + '\\' + file  # 将文件命加入到当前文件路径后面
            # newDir绝对路径
            # print(newDir)
            # path =
            if os.path.isfile(newDir):  # 如果是文件
                # # print('newDir:', newDir)
                if file.startswith('label'):
                    # print(OUTPUT_PATH + '\\' + file)
                    # print(newDir)
                    connet = filepath.split('\\')[-1]
                    # print(OUTPUT_PATH + '\\' + connet)
                    os.makedirs(OUTPUT_PATH + '\\' + connet + '__' + '{}'.format(count))

                    shutil.copy(newDir, OUTPUT_PATH + '\\' + connet + '__' + '{}'.format(count))
                    new_dir_list.append(OUTPUT_PATH + '\\' + connet + '__' + '{}'.format(count))
                    # print(new_dir_list)
                    count += 1
            else:
                eachFile(newDir, OUTPUT_PATH)  # 如果不是文件，递归这个文件夹的路径
        # 复制除label外的文件
        for file in fileNames:
            connet = filepath.split('\\')[-1]
            # print(OUTPUT_PATH + '\\' + connet)
            newDir = filepath + '\\' + file  # 将文件命加入到当前文件路径后面
            if os.path.isfile(newDir):  # 如果是文件
                # # print('newDir:', newDir)
                if not file.startswith('label'):
                    for i in new_dir_list:
                        shutil.copy(newDir, i)
            else:
                eachFile(newDir, OUTPUT_PATH)  # 如果不是文件，递归这个文件夹的路径
    except:
        pass


if __name__ == '__main__':
    filepath = r'D:\dir1'
    OUTPUT_PATH = r'D:\dir2'
    eachFile(filepath, OUTPUT_PATH)
