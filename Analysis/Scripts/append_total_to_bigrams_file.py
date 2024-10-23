import sys

def append_sum_of_percentages(filename):
    total_percentage = 0.0

    # Read the file and calculate the sum of percentages
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            percentage_str = line.split('%')[0].strip()
            if percentage_str:
                total_percentage += float(percentage_str)

    # Append the sum to the end of the file
    with open(filename, 'a') as file:
        file.write(f"\nTotal: {total_percentage:.3f}%\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    input_file = sys.argv[1]
    append_sum_of_percentages(input_file)
