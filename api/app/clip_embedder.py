# clip_model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")
# clip_processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")


from transformers import CLIPModel, CLIPProcessor
import torch


# model = SentenceTransformer("all-MiniLM-L6-v2")

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


# def embed_text(text: str) -> list[float]:

#     with torch.no_grad():

#         inputs = clip_processor(text=text, return_tensors="pt")
#         text_features = clip_model.get_text_features(**inputs)
#         embeddings = text_features / text_features.norm(dim=-1, keepdim=True)

#         return embeddings[0].tolist()


def embed_text(texts: list[str]) -> list[list[float]]:
    """Returns normalized embeddings for a list of input texts."""
    with torch.no_grad():
        inputs = clip_processor(
            text=texts, return_tensors="pt", padding=True, truncation=True
        )
        text_features = clip_model.get_text_features(**inputs)
        embeddings = text_features / text_features.norm(dim=-1, keepdim=True)
        return embeddings.tolist()


if __name__ == "__main__":

    text1 = "a very very unrelated sentence about a comedian"
    text2 = "brown boots"
    text3 = "stilettos"

    output = embed_text([text1, text2])
    # print(output.shape)

    # vec1 = embed_text(text1)
    # print("Text1", text1, vec1[:2])
    # vec2 = embed_text(text2)
    # print("Text2", text2, vec2[:2])
    # vec3 = embed_text(text3)
    # print("Text3", text3, vec3[:2])
    # print(
    #     "cosine sim 1 and 2:",
    #     torch.nn.functional.cosine_similarity(
    #         torch.tensor(vec2), torch.tensor(vec1), dim=0
    #     ).item(),
    # )
    # print(
    #     "cosine sim 2 and 3:",
    #     torch.nn.functional.cosine_similarity(
    #         torch.tensor(vec2), torch.tensor(vec3), dim=0
    #     ).item(),
    # )
    # print(
    #     "cosine sim 1 and 3:",
    #     torch.nn.functional.cosine_similarity(
    #         torch.tensor(vec1), torch.tensor(vec3), dim=0
    #     ).item(),
    # )
