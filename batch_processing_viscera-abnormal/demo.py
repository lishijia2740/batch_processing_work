import os
import shutil


def remove_file(input_path):
    out_dir = os.listdir(input_path)
    # print(out_dir)
    for i in out_dir:
        # print(os.path.join(input_path + '_new', i))
        os.makedirs(os.path.join(input_path + '_new', i))
        new_path = os.path.join(input_path, i)
        for j in os.listdir(new_path):
            if not os.path.isfile(os.path.join(new_path, j)):
                file_path = os.listdir(os.path.join(new_path, j))
                for z in file_path:
                    if os.path.isfile(os.path.join(os.path.join(new_path, j), z)):
                        os.link(os.path.join(os.path.join(new_path, j), z), os.path.join(input_path + '_new', i, z))
    print(input_path + '_new')


if __name__ == '__main__':
    INPUT_PATH = r'D:\dir1'
    remove_file(INPUT_PATH)

