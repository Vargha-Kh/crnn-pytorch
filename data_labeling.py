import pandas as pd
import glob
import time
import shutil


def reading_data():
    df = pd.read_csv('./License Plate/List.csv', header=None)
    data = df.to_numpy()
    path = './License Plate/NR/*.jpg'
    img_dir = sorted(glob.glob(path, recursive=False))
    return data, img_dir


def renaming_files(data, img_dir):
    for i, img in enumerate(data):
        try:
            # [image for img in ]
            if img[0] == str(img_dir[i].split('/')[-1]):
                plates = img[1]
                before = img_dir[i]
                after = "./plates/" + str(i) + '_' + plates + '.jpg'
                shutil.copy(before, after)
        except IndexError as e:
            print(e)
            continue


if __name__ == "__main__":
    start = time.time()
    data, img_dir = reading_data()
    renaming_files(data, img_dir)
    print(f"elapsed processing time: {time.time() - start} sec")
