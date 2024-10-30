import subprocess
import os

# Get the current directory
current_dir = os.getcwd()

# Define the file paths for the output and error log files
output_file = os.path.join(current_dir, "tasklist_output.txt")
error_log = os.path.join(current_dir, "error_log.txt")

# Run the tasklist command and capture the output and errors
try:
    # Providing the full path to tasklist.exe might help with finding the executable
    tasklist_command = r"C:\Windows\System32\tasklist.exe"
    
    result = subprocess.run([tasklist_command], capture_output=True, text=True, check=True)
    
    # Write the output to a text file
    with open(output_file, "w") as file:
        file.write(result.stdout)
    
    print(f"Tasklist has been written to {output_file}")
except subprocess.CalledProcessError as e:
    # Log the error to a file
    with open(error_log, "w") as file:
        file.write(f"An error occurred: {e}\n")
        file.write(f"Standard Error: {e.stderr}\n")

# Wait for the user to press a key before closing
input("Press Enter to exit...")
