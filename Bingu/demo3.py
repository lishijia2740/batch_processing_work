import os
import shutil
"""
现数据格式
    不同窗宽窗位图像加上其剩余按连通域拆分出来的标签，多个图像对应多个标签
        image1,iamge2,iamge3,lable1,label2,label3
        
理想格式
    一个连通域标签对应多个不同窗宽窗位的图像数据
        iamge1,image2,image3,label1
        iamge1,image2,image3,label2
        iamge1,image2,image3,label3

"""

class File_Link():

    def copy_file(self, INPUT_PATH, OUTPUT_PATH):
        fileNames = os.listdir(INPUT_PATH)  # 获取当前路径下的文件名，返回List
        # print(fileNames)
        count = 1
        new_dir_list = []
        #
        for file in fileNames:
            if os.path.isfile(os.path.join(INPUT_PATH, file)):
                if file.startswith('label'):
                    connet = INPUT_PATH.split('\\')[-1]
                    os.makedirs(os.path.join(OUTPUT_PATH, connet + '__' + '{}'.format(count)))
                    shutil.copyfile(os.path.join(INPUT_PATH, file),
                                    os.path.join(OUTPUT_PATH, connet + '__' + '{}'.format(count), file))
                    new_dir_list.append(os.path.join(OUTPUT_PATH, connet + '__' + '{}'.format(count)))
                    count += 1

        for file in fileNames:
            newDir = os.path.join(INPUT_PATH, file)  # 将文件命加入到当前文件路径后面
            if os.path.isfile(newDir):  # 如果是文件
                if not file.startswith('label'):
                    for i in new_dir_list:
                        shutil.copyfile(newDir, os.path.join(i, file))

    def traverse_dir(self, INPUT_PATH, OUTPUT_PATH):
        fileNames = os.listdir(INPUT_PATH)  # 获取当前路径下的文件名，返回List
        for file in fileNames:
            newdir = os.path.join(INPUT_PATH, file)
            self.copy_file(newdir, OUTPUT_PATH)


if __name__ == '__main__':
    filepath = r'D:\dir1'
    OUTPUT_PATH = r'D:\dir2'
    c = File_Link()
    c.traverse_dir(filepath, OUTPUT_PATH)
