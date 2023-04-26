import os
import csv
import shutil
import persian

# Path to the directory containing the files to be renamed
directory_path = "./NR"
output_path = "./plates"
# Path to the CSV label file
label_file_path = "List.csv"

# Open the CSV label file
with open(label_file_path, "r") as label_file:
    # Create a CSV reader object
    csv_reader = csv.reader(label_file)

    # Iterate over each row in the CSV file

    for i, row in enumerate(csv_reader):
        try:
            # Get the old and new file names from the CSV file
            old_name, new_name = row
            new_name = persian.convert_en_numbers(new_name)
            print(i)
            # Construct the full paths to the old and new files

            old_path = os.path.join(directory_path, old_name)
            new_path = os.path.join(output_path, new_name + '.jpg')
            print(old_path, new_path)
            # Rename the file
            shutil.copy(old_path, new_path)
        except Exception as e:
            print(e)
            continue
