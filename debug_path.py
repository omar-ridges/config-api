import urllib.parse

# Test the exact path from the failing test
test_path = "../../../etc/passwd"
print("Original path:", repr(test_path))

# Decode URL encoded characters
decoded_path = urllib.parse.unquote(test_path)
print("Decoded path:", repr(decoded_path))

# Check if it contains ".."
print("Contains ..:", ".." in decoded_path)
print("Starts with /:", decoded_path.startswith("/"))
print("Contains \\:", "\\" in decoded_path)