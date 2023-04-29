import os
import csv
import glob
import random
import math
import shutil
import persian


def transfer_directory_items(in_dir, out_dir, transfer_list, mode='cp', remove_out_dir=False):
    print(f'starting to copying/moving from {in_dir} to {out_dir}')
    if remove_out_dir or os.path.isdir(out_dir):
        os.system(f'rm -rf {out_dir}; mkdir -p {out_dir}')
    if mode == 'cp':
        for name in transfer_list:
            shutil.copy(os.path.join(in_dir, name), out_dir)
    elif mode == 'mv':
        for name in transfer_list:
            shutil.move(os.path.join(in_dir, name), out_dir)
    else:
        raise ValueError(f'{mode} is not supported, supported modes: mv and cp')
    print(f'finished copying/moving from {in_dir} to {out_dir}')


def dir_train_test_split(in_dir, out_dir, test_size=0.3, result_names=('train', 'val'), mode='cp',
                         remove_out_dir=False):
    from sklearn.model_selection import train_test_split
    list_ = os.listdir(in_dir)
    train_name, val_name = train_test_split(list_, test_size=test_size)
    transfer_directory_items(in_dir,
                             os.path.join(out_dir, result_names[0]),
                             train_name, mode=mode,
                             remove_out_dir=remove_out_dir)
    transfer_directory_items(in_dir,
                             os.path.join(out_dir, result_names[1]),
                             val_name, mode=mode,
                             remove_out_dir=remove_out_dir)


def renaming_label_file_csv(label_file_path="List.csv", directory_path="./NR", output_path="./plates"):
    # Open the CSV label file
    with open(label_file_path, "r") as label_file:
        # Create a CSV reader object
        csv_reader = csv.reader(label_file)

        # Checking whether the output dir is made or not
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        # Iterate over each row in the CSV file
        for i, row in enumerate(csv_reader):
            try:
                # Get the old and new file names from the CSV file
                old_name, new_name = row
                new_name = persian.convert_en_numbers(new_name)

                # Construct the full paths to the old and new files
                old_path = os.path.join(directory_path, old_name)
                new_path = os.path.join(output_path, new_name + '.jpg')

                print(f"[INFO: {i}] Copying from {old_path} into {new_path}")
                # Rename the file
                shutil.copy(old_path, new_path)
            except Exception as e:
                print(e)
                continue


if __name__ == "__main__":
    # set the Path to the directory containing the files to be renamed hardcoded
    directory_path = "./NR"
    output_path = "./plates"
    # Path to the CSV label file
    label_file_path = "List.csv"
    # renaming_label_file_csv(label_file_path, directory_path, output_path)

    # Splitting datasets
    dir_train_test_split(output_path, "./datasets")
