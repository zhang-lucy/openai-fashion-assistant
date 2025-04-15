from openai import OpenAI
import os
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FASHION_QUERY_PROMPT = """
You are an expert fashion stylist. Your task is to extract the item category and relevant style tags from a user's query.

Let's think step by step.
Input: "{query}"

Step 1: Identify what category of clothing or items are mentioned. If no specific items are mentioned, leave it blank.
Step 2: Identify descriptors, aesthetics, seasons, or occasions mentioned.
Step 3: Format the output as:
Category: <comma-separated list>
Tags: <comma-separated list>
""".strip()


def postprocess(items: List[str], disallow_prefix: str = "") -> List[str]:
    clean = [i.lower().strip() for i in items if i]
    if disallow_prefix:
        clean = [i for i in clean if not i.startswith(disallow_prefix)]
    return list(dict.fromkeys(clean))  # dedupe


def parse_query(query: str) -> Dict[str, List[str]]:
    prompt = FASHION_QUERY_PROMPT.replace("{query}", query)
    # print("PROMPT:\n", prompt)

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",  # or your version
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content
    # print("RESPONSE:\n", content)

    category_match = re.search(r"Category:\s*(.+)", content, re.IGNORECASE)
    tags_match = re.search(r"Tags:\s*(.+)", content, re.IGNORECASE)

    raw_categories = category_match.group(1).split(",") if category_match else []
    raw_tags = tags_match.group(1).split(",") if tags_match else []

    return {
        "category": postprocess(raw_categories, disallow_prefix="tags:"),
        "tags": postprocess(raw_tags),
    }


if __name__ == "__main__":
    result = parse_query(
        "Looking for a minimalist black crossbody bag for summer travel"
    )
    print("Parsed Category:", result["category"])
    print("Parsed Tags:", result["tags"])
