import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askdirectory
import os

# Initialize Tk
Tk().withdraw()

# Prompt the user to select the respective files for baro and transducer
baro_files = askopenfilenames(title="Select baro files")
transducer_files = askopenfilenames(title="Select transducer files")

# Sort the files based on the date suffix
baro_files = sorted(baro_files)
transducer_files = sorted(transducer_files)

# Prompt the user to specify a directory for the exported CSV files
save_directory = askdirectory(title="Select directory to save the files")

# Baro data
first_file = True
for file in baro_files:
    if first_file:
        # For the first file, retain the data
        baro_data = pd.read_csv(file, skiprows=10, encoding='ISO-8859-1')
        first_file = False
    else:
        # For the other files, remove the metadata and append the data to the first file
        temp_data = pd.read_csv(file, skiprows=10, encoding='ISO-8859-1')
        baro_data = pd.concat([baro_data, temp_data], ignore_index=True, axis=0)

# Save the merged baro data to the specified directory
baro_save_path = os.path.join(save_directory, 'Baro_Merged.csv')
baro_data.to_csv(baro_save_path, index=False)

# Transducer data
grouped_files = {}
for file in transducer_files:
    # Group all files by checking the second line of each CSV file to check if the serial numbers match
    metadata = pd.read_csv(file, nrows=10, header=None, encoding='ISO-8859-1')
    serial_number = metadata.iloc[1,0]
    location = metadata.iloc[5,0]
    if serial_number not in grouped_files:
        grouped_files[serial_number] = {'location': location, 'files': [file]}
    else:
        grouped_files[serial_number]['files'].append(file)

for serial_number, data in grouped_files.items():
    first_file = True
    for file in data['files']:
        if first_file:
            # For the first file, retain the data
            transducer_data = pd.read_csv(file, skiprows=11, encoding='ISO-8859-1')
            first_file = False
        else:
            # For the other files, remove the metadata and append the data to the first file
            temp_data = pd.read_csv(file, skiprows=11, encoding='ISO-8859-1')
            transducer_data = pd.concat([transducer_data, temp_data], ignore_index=True, axis=0)
    # Save the merged transducer data to the specified directory
    transducer_save_path = os.path.join(save_directory, f'{serial_number}_{data["location"]}_Merged.csv')
    transducer_data.to_csv(transducer_save_path, index=False)