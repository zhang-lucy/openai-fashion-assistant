from app.parse_query import parse_query
from app.clip_embedder import embed_text
from app.schemas import Product as ProductSchema
from sqlalchemy import text
from collections import defaultdict
RERANKING_CONFIG = {
    "no_photo": {"weight": -0.5},
    "marked_for_archive": {"weight": -1},
    "high_average_rating": {
        "threshold": 4,
        "normalization_constant": 5,
        "weight": 0.5,
    },
    "low_average_rating": {
        "threshold": 2,
        "normalization_constant": 2,
        "weight": -0.5,
    },
    "high_rating_number": {
        "threshold": 30,
        "ceiling": 200,
        "normalization_constant": 200,
        "weight": 0.2,
    },
}

MAX_KEYWORDS = 2

EMPTY_TOKEN = "UNKNOWN"

EMBEDDINGS_MATCH_WEIGHT = 1
TITLE_MATCH_WEIGHT = 0.5


class SearchService:
    def __init__(self, user_preferences: dict):
        self.user_preferences = user_preferences

    def search_products(self, q: str, db):
        # Parse categories and relevant tags from query
        parsed = parse_query(q)
        print("Parsed query", parsed)
        keywords_for_title_search = parsed.get("category", []) + parsed.get("tags", [])

        query_with_preferences = self._add_user_preferences(parsed)
        print("Query with preferences", query_with_preferences)

        formatted_query = self._format_query(query_with_preferences)
        print("Formatted query", formatted_query)

        ## TODO: Run both retrieval methods in parallel
        
        # Embeddings search
        embedding = embed_text(formatted_query)[0]
        retrieved_embeddings_products = self._embeddings_search(embedding, db)
        print(f"Retrieved {len(retrieved_embeddings_products)} products from embeddings search")

        # Title search on keywords
        print("Keywords for title search", keywords_for_title_search)
        retrieved_title_products = self._title_search(keywords_for_title_search, db)
        print(f"Retrieved {len(retrieved_title_products)} products from title search")

        # De-dupe and merge results
        merged_products = self._merge_results(retrieved_embeddings_products, retrieved_title_products)

        products = self._rerank_products(merged_products)
        print(f"Reranked {len(products)} products")

        return products
    
    def _add_user_preferences(self, parsed_query):
        # Try catch so we don't fail on this
        try:
            if self.user_preferences:
                # Add gender
                if self.user_preferences.gender:
                    parsed_query["gender"] = [self.user_preferences.gender.lower()]
                else:
                    parsed_query["gender"] = [EMPTY_TOKEN]

                # Add styles
                if self.user_preferences.styles:
                    # Append styles to tags
                    if parsed_query.get("tags") is None:
                        parsed_query["style"] = self.user_preferences.styles
                    else:
                        parsed_query["style"].extend(self.user_preferences.styles)
                return parsed_query
            else:
                return parsed_query
        except Exception as e:
            print("Error adding user preferences", e)
            return parsed_query
    
    def _format_query(self, parsed):
        # Order these gender, category, styles
        # Python maintains the order of the keys
        formatted_query = {}
        if parsed.get("gender"):
            formatted_query["gender"] = parsed["gender"]
        else:
            formatted_query["gender"] = [EMPTY_TOKEN]

        # Add colors
        # TODO: Extract colors from query
        formatted_query["colors"] = [EMPTY_TOKEN]

        if parsed.get("category"):
            formatted_query["category"] = parsed["category"]
        else:
            formatted_query["category"] = [EMPTY_TOKEN]

        if parsed.get("tags"):
            formatted_query["styles"] = parsed["tags"]
        else:
            formatted_query["styles"] = [EMPTY_TOKEN]

        return str(formatted_query)

    def _embeddings_search(self, embedding, db):
        command = text(
            f"""
            SELECT id, 1 - (embedding <=> '{embedding}') AS similarity, title, "imageUrls", average_rating, rating_number, store, "createdAt", "modifiedAt", "deletedAt", description FROM products
            WHERE embedding IS NOT NULL AND "deletedAt" IS NULL
            ORDER BY embedding <=> '{embedding}'
            LIMIT 100;
        """
        )
        result = db.execute(command).fetchall()

        retrieved_products = [ProductSchema.from_orm(row) for row in result]
        return retrieved_products

    def _title_search(self, keywords: list[str], db):
        try:
            if len(keywords) == 0:
                return []
            keywords_match_str = " AND ".join([f"title ILIKE '%{keyword}%'" for keyword in keywords[:MAX_KEYWORDS]])
            command = text(
                f"""
                SELECT id, 1 as similarity, title, "imageUrls", average_rating, rating_number, store, "createdAt", "modifiedAt", "deletedAt", description FROM products
                WHERE {keywords_match_str} AND "deletedAt" IS NULL
                LIMIT 100;
            """
            )
            result = db.execute(command).fetchall()
            retrieved_products = [ProductSchema.from_orm(row) for row in result]
            return retrieved_products
        except Exception as e:
            print("Error in title search", e)
            return []
    
    def _merge_results(self, embeddings_products, title_products):
        # Combine and add scores if they appear in both based on ID match
        id_to_score = defaultdict(float)
        id_to_product = {}
        for product in embeddings_products:
            id_to_score[product.id] += (product.similarity if product.similarity else 0) * EMBEDDINGS_MATCH_WEIGHT
            id_to_product[product.id] = product
        for product in title_products:
            id_to_score[product.id] += (product.similarity if product.similarity else 0) * TITLE_MATCH_WEIGHT
            id_to_product[product.id] = product

        # Sort by score and return
        merged_products = []
        for product_id, score in sorted(id_to_score.items(), key=lambda x: x[1], reverse=True):
            product = id_to_product[product_id]
            product.similarity = score
            merged_products.append(product)

        return merged_products

    def _rerank_products(self, products):
        for product in products:
            score = product.similarity

            # Penalize if the photo is "no image avaialable"
            if len(product.imageUrls) > 0 and product.imageUrls[0] == [
                "https://m.media-amazon.com/images/I/01RmK+J4pJL._AC_.gif"
            ]:
                score += RERANKING_CONFIG["no_photo"]["weight"]

            # Penalize if title marked for archive
            if product.title and product.title == "Marked For Archive":
                score += RERANKING_CONFIG["marked_for_archive"]["weight"]

            # Rule 3: High average rating boost
            avg_rating = product.average_rating if product.average_rating else 0
            if avg_rating >= RERANKING_CONFIG["high_average_rating"]["threshold"]:
                norm_rating = (
                    avg_rating
                    / RERANKING_CONFIG["high_average_rating"]["normalization_constant"]
                )
                score += norm_rating * RERANKING_CONFIG["high_average_rating"]["weight"]

            # Rule 4: Low average rating penalty
            if avg_rating < RERANKING_CONFIG["low_average_rating"]["threshold"]:
                norm_rating = (
                    avg_rating
                    / RERANKING_CONFIG["low_average_rating"]["normalization_constant"]
                )
                score += norm_rating * RERANKING_CONFIG["low_average_rating"]["weight"]

            # Rule 5: High ratings number boost
            rating_number = product.rating_number if product.rating_number else 0
            if rating_number > RERANKING_CONFIG["high_rating_number"]["threshold"]:
                capped_count = min(
                    rating_number, RERANKING_CONFIG["high_rating_number"]["ceiling"]
                )
                norm_count = (
                    capped_count
                    / RERANKING_CONFIG["high_rating_number"]["normalization_constant"]
                )
                score += norm_count * RERANKING_CONFIG["high_rating_number"]["weight"]

            product.similarity = score

        return sorted(products, key=lambda x: x.similarity, reverse=True)


if __name__ == "__main__":

    def test_rerank_products():
        service = SearchService()

        products = [
            # Case 1: No photo penalty
            {
                "similarity": 1.0,
                "rating_number": 0,
                "average_rating": 3,
                "title": "No Photo Item",
                "image_urls": [
                    "https://m.media-amazon.com/images/I/01RmK+J4pJL._AC_.gif"
                ],
            },
            # Case 2: Title "Marked For Archive"
            {
                "similarity": 1.0,
                "rating_number": 0,
                "average_rating": 0,
                "title": "Marked For Archive",
                "image_urls": ["https://example.com/photo.jpg"],
            },
            # Case 3: High average rating boost
            {
                "similarity": 1.0,
                "rating_number": 0,
                "average_rating": 4.5,
                "title": "Great Product",
                "image_urls": ["https://example.com/photo.jpg"],
            },
            # Case 4: Low average rating penalty
            {
                "similarity": 1.0,
                "rating_number": 0,
                "average_rating": 1.5,
                "title": "Bad Product",
                "image_urls": ["https://example.com/photo.jpg"],
            },
            # Case 5: High ratings count boost
            {
                "similarity": 1.0,
                "rating_number": 100,
                "average_rating": 3.0,
                "title": "Popular Product",
                "image_urls": ["https://example.com/photo.jpg"],
            },
            # Case 6: All conditions combined
            {
                "similarity": 1.0,
                "rating_number": 150,
                "average_rating": 4.8,
                "title": "Marked For Archive",
                "image_urls": [
                    "https://m.media-amazon.com/images/I/01RmK+J4pJL._AC_.gif"
                ],
            },
        ]

        ranked = service._rerank_products(products)

        for p in ranked:
            print(f"{p['title']} => similarity: {p['similarity']:.3f}")

    test_rerank_products()
