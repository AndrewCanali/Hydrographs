Groundwater Elevation Analysis

This Python script is used to process and analyze groundwater elevation data. It reads data from multiple CSV and Excel files, performs various calculations, and generates a plot of the groundwater elevation over time.

## Dependencies

The script requires the following Python libraries:

- pandas
- matplotlib
- numpy
- tkinter
- os

## Constants

The script uses the following constants:

- FONT_NAME: The font name used in the plot. Default is "Arial".
- FONT_SIZE: The font size used in the plot. Default is 12.
- CONVERSION_FACTOR: The conversion factor used to convert pressure readings from kilopascals to meters of water. Default is 0.101972.
- DATE_FORMAT: The date format used in the data files. Default is '%m/%d/%Y %H:%M:%S'.

## User Inputs

The script prompts the user to select the following Excel files:

- Lookup.xlsx: Contains lookup information for each data file.
- Offsets.xlsx: Contains offset values to be applied to the data.
- Turnbull_EQuIS_WaterLevels_20240501.xlsx: Contains manual groundwater elevation measurements.
- ErroneousData.xlsx: Contains information about erroneous data that should be omitted from the analysis.

The script also prompts the user to select one or more CSV files containing the groundwater elevation data.

## Output

The script generates a plot of the groundwater elevation over time for each location. The plot includes both the calculated groundwater elevation and the manual measurements. The plot is displayed on the screen.

The script also writes several CSV files containing intermediate and final results of the calculations.

## Notes

- The script assumes that the data files are in a specific format. If your data files are in a different format, you may need to modify the script.
- The script performs several checks and prints out messages if it encounters any issues. Please pay attention to these messages as they may indicate problems with the data or the calculations.
- The script uses the tkinter library to prompt the user to select the data files. This means that it requires a graphical user interface (GUI) to run. If you are running the script on a server or other environment without a GUI, you may need to modify the script to specify the data files in a different way.
