import json

input_file = "meta_Amazon_Fashion_100.jsonl"
output_file = "meta_Amazon_Fashion_100.json"

data_list = []

# Read JSONL file line by line
with open(input_file, "r") as f:
    for line in f:
        if line.strip():  # skip empty lines
            data_list.append(json.loads(line))

# Write to JSON file with key "data"
with open(output_file, "w") as f:
    json.dump({"data": data_list}, f, indent=2)

print(f"Wrapped {len(data_list)} items under 'data' in {output_file}")
