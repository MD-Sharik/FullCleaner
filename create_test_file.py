import hashlib
import os

# Create a test file with known content that our antivirus will detect
test_content = b"TEST-MALWARE-SIGNATURE-DO-NOT-PANIC"

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
test_file_path = os.path.join(script_dir, "test_malware.txt")

# Save it to a file
with open(test_file_path, "wb") as f:
    f.write(test_content)

# Calculate and display its hash
test_hash = hashlib.sha1(test_content).hexdigest()
print(f"Created test file at: {test_file_path}")
print(f"SHA-1 hash: {test_hash}")
print("\nThis file contains a harmless test signature that the antivirus will detect.")
print("You can now test the antivirus by scanning the folder containing this file using Custom Scan.")