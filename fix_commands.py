
import os

file_path = r'c:\Users\91700\Downloads\old repo custimize\NBBotz-Auto-Filter-Bot\plugins\commands.py'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Find the start of the messed up block
# It starts after line 39 (m = message)
# And ends before line 48 (settings = ...)

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "m = message" in line:
        start_idx = i + 1
    if "settings = await get_settings(grp_id)" in line:
        end_idx = i
        if start_idx != -1:
            break

if start_idx != -1 and end_idx != -1:
    print(f"Found block from line {start_idx+1} to {end_idx}")
    
    # Verify the content is messed up (has multiple 'if len...')
    block = lines[start_idx:end_idx]
    count = sum(1 for l in block if "if len(m.command) == 2" in l)
    print(f"Number of duplicate 'if' lines in block: {count}")
    
    if count > 0:
        # Create the correct block
        correct_block = [
            "    if len(m.command) == 2 and m.command[1].startswith(('notcopy', 'sendall')):\n",
            "        _, userid, verify_id, file_id = m.command[1].split(\"_\", 3)\n",
            "        user_id = int(userid)\n",
            "        grp_id = temp.VERIFICATIONS.get(user_id, 0)\n",
            "    \n"
        ]
        
        # Replace the messy block with the correct one
        new_lines = lines[:start_idx] + correct_block + lines[end_idx:]
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("File patched successfully.")
        except Exception as e:
            print(f"Error writing file: {e}")
    else:
        print("Block doesn't seem to contain duplicates. Skipping.")
else:
    print("Could not find start or end markers.")
