import csv
import re

def process_iron_ingots(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    data = []
    current_time = None

    for line in lines:
        # Check for the "Items for lime" line and extract time
        time_match = re.search(r"Items for lime \(([\d.]+) min\)", line)
        if time_match:
            current_time = time_match.group(1)

        # Check for the "Iron Ingot" line and extract count
        ingot_match = re.search(r"- Iron Ingot: (\d+)", line)
        if ingot_match and current_time is not None:
            iron_ingots = ingot_match.group(1)
            data.append((iron_ingots, current_time))
            current_time = None  # Reset after using

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['items', 'minutes'])
        writer.writerows(data)

    print(f"Done! {len(data)} rows written to '{output_file}'.")

# Define the input and output files
input_file = '/root/Projects/Minecraft/chat.txt'  # Replace with the actual path to your text file
output_file = '/root/Projects/Minecraft/iron_ingots_2e.csv'

# Run the process function
process_iron_ingots(input_file, output_file)


