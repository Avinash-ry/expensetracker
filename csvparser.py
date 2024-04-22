import csv
from itertools import islice

def parse_csv(file_path, header_row, data_start_row):
    """Parse a CSV file and print each row line by line, using the specified header row for field names
       and reinserting these headers at the top of the data slice."""
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            headers = []
            data = []
            csv_reader = csv.reader(file)

            # Reading up to the header row and saving headers
            for i, row in enumerate(csv_reader):
                if i == header_row - 1:
                    headers = row
                    break

            # Skipping rows until the data start row
            for i, row in enumerate(csv_reader, start=header_row):
                if i >= data_start_row - 1:
                    data.append(row)

            # Display or process the data with headers
            print(headers)  # Print headers first
            for row in data:
                # Creating a dictionary for each row, associating with headers
                row_dict = dict(zip(headers, row))
                print(row_dict)

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
file_path = 'sbi.xls'  # The path to your CSV file
header_row = int(input("Enter the line number for the header row: "))  # Get user input for the header row
data_start_row = int(input("Enter the line number where the data begins: "))  # Get user input for the data start row
parse_csv(file_path, header_row, data_start_row)
