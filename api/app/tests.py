from transformers import CLIPModel, CLIPProcessor
import torch
from tabulate import tabulate


clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def embed_text(text: str) -> list[float]:

    with torch.no_grad():

        inputs = clip_processor(text=text, return_tensors="pt")
        text_features = clip_model.get_text_features(**inputs)
        embeddings = text_features / text_features.norm(dim=-1, keepdim=True)

        return embeddings[0].tolist()


def cosine_similarity(vec1, vec2):
    v1 = torch.tensor(vec1)
    v2 = torch.tensor(vec2)
    return torch.nn.functional.cosine_similarity(v1, v2, dim=0).item()


def run_tests():
    test_cases = [
        # ("brown boots", "leather ankle boots", True),
        # ("stilettos", "high heels", True),
        # ("cute dress with ruffles", "brown boots", False),
        # ("a comedian at a club", "brown boots", False),
        # ("black sneakers", "running shoes", True),
        # ("stiletto heels", "a very funny podcast", False),
        # (
        #     "YUEDGE 5 Pairs Men's Moisture Control Cushioned Dry Fit Casual Athletic Crew Socks for Men (Blue, Size 9-12)",
        #     "RONNOX Women's 3-Pairs Bright Colored Calf Compression Tube Sleeves",
        #     True,
        # ),
        # (
        #     "DouBCQ Women's Palazzo Lounge Wide Leg Casual Flowy Pants(Flower Mix Blue, XL)",
        #     "JXG Women Classic Linen Casual African Dashiki Print Baggy Wide Leg Pants Purple US 3XL",
        #     True,
        # ),
        (
            '{"gender":["women"], "categories": [stiletto heels]}',
            '{"gender":["women"], "categories":[thong, sandal]}',
            True,
        ),
        (
            '{"gender":["women"], "colors": ["blue"], "categories": ["shorts"], "styles": [jeans]}',
            '{"gender":["women"], "categories":[pants], "styles": [lounge, wide, leg, casual, flowy]}',
            True,
        ),
        (
            '{"gender":["men"], "colors": ["blue"], "categories": ["shorts"]}',
            '{"gender":["women"], "categories":[pants], "styles": [lounge, wide, leg, casual, flowy]}',
            True,
        ),
    ]

    results = []
    threshold_similar = 0.75
    threshold_dissimilar = 0.74

    for text1, text2, should_be_similar in test_cases:
        vec1 = embed_text(text1)
        vec2 = embed_text(text2)
        sim = cosine_similarity(vec1, vec2)
        passed = (
            sim >= threshold_similar
            if should_be_similar
            else sim < threshold_dissimilar
        )
        results.append(
            [
                text1[:50],
                text2[:50],
                f"{sim:.3f}",
                "✅" if passed else "❌",
                "Expect Similar" if should_be_similar else "Expect Dissimilar",
            ]
        )

    print(
        tabulate(
            results,
            headers=["Text A", "Text B", "Cosine Similarity", "Pass", "Expectation"],
            tablefmt="github",
        )
    )


if __name__ == "__main__":
    run_tests()
