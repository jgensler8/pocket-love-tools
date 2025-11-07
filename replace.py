import re

input_file = "Pocket_Love_If_1999_KID_JP.ngc"
output_file = "pocklove_replaced.ngc"

# search_pattern = b'\xb0\x00' # Note the 'b' prefix for byte string
# search_pattern = b'\xb0' # Note the 'b' prefix for byte string

# search_pattern = b'\xb0\x00' # Note the 'b' prefix for byte string
# search_pattern = b'\xb0' # Note the 'b' prefix for byte string

# failed: replace ha ha <3 with all hearts
search_pattern = b'\x00\x86\x00\x86'
replace_pattern = b'\x00\xee\x00\xee'
# search_pattern = b'\x86'
# replace_pattern = b'\xee'

with open(input_file, 'rb') as f_in:
    data = f_in.read()

# Replace all occurrences
modified_data = data.replace(search_pattern, replace_pattern)

# Or, if using regex (more flexible for complex patterns):
# modified_data = re.sub(re.escape(search_pattern), replace_pattern, data)

with open(output_file, 'wb') as f_out:
    f_out.write(modified_data)

print(f"Binary data replaced in {input_file} and saved to {output_file}")