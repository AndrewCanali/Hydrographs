import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import matplotlib as mpl
from tkinter import filedialog
from tkinter import Tk
import os

# Set constants
FONT_NAME = "Arial"
FONT_SIZE = 12
CONVERSION_FACTOR = 0.101972
DATE_FORMAT = '%m/%d/%Y %H:%M:%S'  # Set this to your desired date format

# Set the default font and size
mpl.rcParams['font.sans-serif'] = FONT_NAME
mpl.rcParams['font.size'] = FONT_SIZE

# Prompt the user to select the Lookup.xlsx file
root = Tk()
root.withdraw()  # Hide the main window
lookup_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])  # Show the file dialog
lookup = pd.read_excel(lookup_file)

# Prompt the user to select the Offsets.xlsx file
offsets_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])  # Show the file dialog
offsets = pd.read_excel(offsets_file)

# Convert 'From' and 'To' columns to datetime and 'Serial_Number' to string
offsets['From'] = pd.to_datetime(offsets['From'], format=DATE_FORMAT)
offsets['To'] = pd.to_datetime(offsets['To'], format=DATE_FORMAT)
offsets['Serial_Number'] = offsets['Serial_Number'].astype(str)

# Prompt the user to select the Turnbull_EQuIS_WaterLevels_20240501.xlsx file
manual_measurements_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])  # Show the file dialog
manual_measurements = pd.read_excel(manual_measurements_file, sheet_name='GW_Elevations')

# Prompt the user to select the ErroneousData.xlsx file
erroneous_data_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])  # Show the file dialog
erroneous_data = pd.read_excel(erroneous_data_file)

# Convert 'From' and 'To' columns to datetime and 'Serial_Number' to string
erroneous_data['From'] = pd.to_datetime(erroneous_data['From'], format=DATE_FORMAT)
erroneous_data['To'] = pd.to_datetime(erroneous_data['To'], format=DATE_FORMAT)
erroneous_data['Serial_Number'] = erroneous_data['Serial_Number'].astype(str)

# Prompt the user to select the files
root = Tk()
root.withdraw()  # Hide the main window
csv_files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])  # Show the file dialog

# Initialize empty dataframe to store all data
all_data = pd.DataFrame()

# Initialize baro_data
baro_data = None

# Process each csv file
for file in csv_files:
    # Get the file name
    file_name = os.path.basename(file)

    # Check if this is the Baro file
    if file_name.startswith("Baro"):
        id = 'Baro'
        # Load csv file
        data = pd.read_csv(file, encoding='ISO-8859-1')
        data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format=DATE_FORMAT)
        data.set_index('DateTime', inplace=True)
        numeric_data = data.select_dtypes(include=[np.number])  # Select only numeric columns
        numeric_data = numeric_data.resample('h').mean().fillna(method='ffill')
        baro_data = numeric_data
        baro_data['LEVEL'] = numeric_data['LEVEL'] * CONVERSION_FACTOR  # Convert from kilopascals to meters of water
        print(f"First line of baro_data for file {file}:\n{baro_data.iloc[0]}")
        # Write baro_data to a CSV file
        baro_data.to_csv(f'{id}_baro_data.csv')
        break

for file in csv_files:
    # Get the file name
    file_name = os.path.basename(file)

    # Skip the Baro file
    if file_name.startswith("Baro"):
        continue

    # Extract the serial number from the file name
    serial_number = file_name[:7]

    # Get corresponding row from lookup table
    lookup_row = lookup[lookup['Serial_Number'].astype(str) == serial_number]

    # Check if lookup_row is empty
    if lookup_row.empty:
        print(f"No matching serial number found in lookup table for file {file}")
        continue

    # Get the ID for this row
    id = lookup_row['ID'].values[0]

    # Load csv file
    data = pd.read_csv(file, encoding='ISO-8859-1')
    data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format=DATE_FORMAT)
    data.set_index('DateTime', inplace=True)
    numeric_data = data.select_dtypes(include=[np.number])  # Select only numeric columns
    numeric_data = numeric_data.resample('h').mean().fillna(method='ffill')

    if baro_data is None:
        print(f"No Baro data found for file {file}")
        continue
    # Resample baro_data to the same frequency as numeric_data and fill NaN values with the same method
    baro_data = baro_data.select_dtypes(include=[np.number]).resample('h').mean().fillna(method='ffill')
    # Check if baro_data['LEVEL'] contains NaN values and fill them with 0
    print(baro_data['LEVEL'].isnull().sum())
    baro_data['LEVEL'].fillna(0, inplace=True)
    # Reindex numeric_data to the index of baro_data
    numeric_data = numeric_data.reindex(baro_data.index)
    data['LEVEL'] = numeric_data['LEVEL'] - baro_data['LEVEL']
    print(f"First line of data after barometric pressure correction for file {file}:\n{data.iloc[0]}")
    # Write the results of the barometric pressure correction to a CSV file
    data[['LEVEL']].to_csv(f'{serial_number}_{id}_barometric_pressure_correction.csv')

    # Check if lookup_row['GW_Elevation_1'].values[0] is NaN
    print(pd.isnull(lookup_row['GW_Elevation_1'].values[0]))

    # Check if data['LEVEL'] contains values that are greater than lookup_row['GW_Elevation_1'].values[0]
    print((data['LEVEL'] > lookup_row['GW_Elevation_1'].values[0]).sum())

    # Print the "GW_Elevation_1" value returned from the lookup
    print(f"GW_Elevation_1 value: {lookup_row['GW_Elevation_1'].values[0]}")

    # Check if numeric_data['LEVEL'].iloc[0] or baro_data['LEVEL'].iloc[0] is NaN
    if pd.isnull(numeric_data['LEVEL'].iloc[0]) or pd.isnull(baro_data['LEVEL'].iloc[0]):
        print(f"Missing data in file {file}")
        continue

    for _, erroneous_row in erroneous_data[(erroneous_data['Serial_Number'] == serial_number) & (erroneous_data['ID'] == id)].iterrows():
            mask = (data.index >= erroneous_row['From']) & (data.index <= erroneous_row['To'])
            data = data[~mask]

    # Initialize transducers_elevation
    transducers_elevation = None

    # Convert data.index to a DatetimeIndex
    data.index = pd.to_datetime(data.index)

    # Calculate the Transducers_Elevation for each matching date, time, and serial number
    print(
        f"Date_1: {lookup_row['Date_1'].values[0]}, Time_1: {lookup_row['Time_1'].values[0]}, Serial_Number: {serial_number}")
    lookup_row['DateTime'] = pd.to_datetime(lookup_row['Date_1'].astype(str) + ' ' + lookup_row['Time_1'].astype(str),
                                            format="%Y-%m-%d %H:%M:%S")
    matching_date_time = lookup_row['DateTime'].values[0]

    # Print out the values for debugging
    print(f"matching_date_time: {matching_date_time}")
    print(f"data.index: {data.index}")
    print(f"serial_number: {serial_number}")
    print(f"lookup_row['Serial_Number'].values[0]: {lookup_row['Serial_Number'].values[0]}")

    # Debugging code
    print(f"Type of serial_number: {type(serial_number)}, length: {len(serial_number)}")
    print(
        f"Type of lookup_row['Serial_Number'].values[0]: {type(lookup_row['Serial_Number'].values[0])}, length: {len(str(lookup_row['Serial_Number'].values[0]))}")

    # Check if the matching_date_time is in data.index
    if matching_date_time in data.index:
        # Get the baro_corrected_level for the matching_date_time
        baro_corrected_level = data.loc[matching_date_time, 'LEVEL']
        print(f"Barometric Corrected LEVEL: {baro_corrected_level}")

        # Calculate the Transducers_Elevation only if the serial number matches
        if str(lookup_row['Serial_Number'].values[0]).strip() == str(serial_number).strip():
            transducers_elevation = lookup_row['GW_Elevation_1'].values[0] - baro_corrected_level
            print(f"Transducers_Elevation: {transducers_elevation}")
        else:
            print(
                f"Serial number {serial_number} does not match with the lookup table serial number {lookup_row['Serial_Number'].values[0]}")
    else:
        print(f"matching_date_time {matching_date_time} not found in data.index")

    # Get corresponding rows from offset table
    offset_rows = offsets[(offsets['Serial_Number'] == serial_number) & (offsets['ID'] == id)]

    # Apply offsets
    for _, offset_row in offsets[(offsets['Serial_Number'] == serial_number) & (offsets['ID'] == id)].iterrows():
        mask = (data.index >= offset_row['From']) & (data.index <= offset_row['To'])
        data.loc[mask, 'LEVEL'] += offset_row['Offsets']

    # Perform datum correction
    data['Transducers_Elevation'] = transducers_elevation
    data['GW_Elevation_masl'] = data['Transducers_Elevation'] + data['LEVEL']
    print(f"First line of data after datum correction for file {file}:\n{data.iloc[0]}")
    # Write the results of the datum correction to a CSV file
    data[['Transducers_Elevation', 'GW_Elevation_masl']].to_csv(f'{id}_datum_correction.csv')

    # Add corrected data to all_data dataframe
    all_data[id] = data['GW_Elevation_masl']

    #Omit erroneous data
    for _, erroneous_row in erroneous_data[
        (erroneous_data['Serial_Number'] == serial_number) & (erroneous_data['ID'] == id)].iterrows():
        mask = (all_data.index >= erroneous_row['From']) & (all_data.index <= erroneous_row['To'])
        omitted_data = all_data.loc[mask, id]

        # Print the omitted data for each location
        print(f"Omitted data for {id} from {erroneous_row['From']} to {erroneous_row['To']}:")
        print(omitted_data)

        all_data.loc[mask, id] = np.nan

# Plot data
plt.figure(figsize=(10, 6))
for column in all_data.columns:
    plt.plot(all_data.index, all_data[column], label=column, linewidth=3)  # Increase the thickness of the lines series being plotted
    # Plot manual measurements
    manual_measurements_for_id = manual_measurements[manual_measurements['ID'] == column]
    plt.scatter(manual_measurements_for_id['measurement_date'], manual_measurements_for_id['GW_Elevation'], marker='s', edgecolors='black', label=f'{column} Manual')

plt.title('')
plt.xlabel('Date', fontweight='bold')  # Bold the X axis label title
plt.ylabel('Elevation (masl)', fontweight='bold')  # Bold the Y axis label title
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format x-axis as "yyyy-mm-dd"
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))  # Set major ticks interval to number of days
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Set major ticks interval to number of months
plt.gcf().autofmt_xdate()  # Rotate date labels automatically
plt.ylim(1660, 1686)  # Set y-axis limits

# Set a fixed start and end date for the x-axis
start_date = pd.to_datetime('12/01/2022')
end_date = pd.to_datetime('01/01/2024')
plt.gca().set_xlim([start_date, end_date])

# Force the plot to label the start and end points on the x-axis
#plt.gca().set_xticks([start_date, end_date])

# Place the legend below the plot with entries shown horizontally
# 'upper center' places the legend below the plot
# bbox_to_anchor places the legend at the specified location
# ncol sets the number of columns in the legend
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(all_data.columns)*2)

plt.tight_layout()
plt.show()