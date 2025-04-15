import json
import random


def sample_jsonl(input_file, output_file, sample_size=10000):
    with open(input_file, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    # Ensure we don't sample more than available lines
    sample_size = min(sample_size, len(lines))
    sampled_lines = random.sample(lines, sample_size)

    with open(output_file, "w", encoding="utf-8") as outfile:
        for line in sampled_lines:
            json_obj = json.loads(line)  # Validate it's valid JSON
            outfile.write(json.dumps(json_obj) + "\n")


if __name__ == "__main__":
    input_path = "details.jsonl"  # replace with your input file path
    output_path = "details_10000.jsonl"  # replace with your desired output file path
    sample_jsonl(input_path, output_path)
