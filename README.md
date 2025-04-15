# 🌟 Fashion Assistant

Welcome to your fashion assistant! File structure:

1. `frontend` - lightweight frontend built using React + Tailwind
2. `api` - microservice with FastAPI + SQLAlchemy
3. `data_processing` - Jupyter Notebooks + additional analysis

## Getting Started

### Frontend

```
cd frontend
npm install
npm run dev
```

### API

```
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

First, you'll need to spin up and seed the database. We've provided a JSON with 100 sample items. The docker-compose.yml file provided will provision a Postgres database locally.

```
docker compose up -d
python -m app.seed
python -m app.upsert_embeddings
```

Now, start the server:

```
python -m uvicorn app.main:app --reload
```

## API Docs

### POST `/products/search`

This endpoint allows you to search for products using any English natural language query. For example, to search "I need a cute dress for the summer":

```
curl -X POST "http://localhost:8000/products/search?q\=I%20need%20a%20cute%20dress%20for%20summer"
-H "Content-Type: application/json"
```

Additionally, you can also pass in search preferences:

```
curl -X POST "http://localhost:8000/products/search?q=\=I%20need%20a%20cute%20dress%20for%20summer" \
-H "Content-Type: application/json" \
-d '{
"gender": "female",
"price": "luxury",
"styles": ["casual", "sporty"]
}'
```

**Parameters**:

- q (required, query parameter): The search term.
- preferences (optional, JSON body):
  - gender (string, e.g. "male" or "female"),
  - price (string, e.g. "budget", "mid-range", "luxury"),
  - styles (array of strings, e.g. ["casual", "formal"]).

**Response**:
The API returns a list of Product objects, as well as a `similarity` score. Schema details can be found in `api/app/models.py`. Sample Product:

```
{
  "id": "dokotoo-womens-high-waist-bell-bottom-jeans-zipper-fly-flared-denim-pants-with-pockets-brown-size-4-B0BDQTRDCN",
  "title": "Dokotoo Womens High Waist Bell Bottom Jeans Zipper Fly Flared Denim Pants with Pockets Brown Size 4",
  "imageUrls": [
    "https://m.media-amazon.com/images/I/31yShJhVRnL._AC_.jpg"
  ],
  "description": "A pair of high waisted pants",
  "details": "",
  "features": [],
  "average_rating": 3.6,
  "rating_number": 3,
  "store": "Dokotoo",
  "createdAt": "2025-04-13T21:57:31.785073+00",
  "modifiedAt": "2025-04-14T04:34:17.946943+00",
  "deletedAt": null,
  "embedding": <length 512 vector>
}
```

## Technical Details

![architecture diagram](backend_architecture.png)

Flow of the request:

- [Query parsing](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/parse_query.py): The natural language query is parsed into a JSON blob of `category` and `tags`, where category represents broader fashion categories like "dress", "shirts", etc. while tags are other miscellaneous styles such as "casual", "denim". Prompt engineering + iteration in [this notebook](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/data_processing/query_parsing.ipynb).
- [Bonus: Personalization](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/search.py#L71-L93): The client can optionally pass in a JSON blob with user preferences, that are used to enhance the input query in the event that these tags cannot be extracted.
- [Query Formatting](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/search.py#L95): The enhanced query is parsed into standard format for embedding
- [Embedding](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/clip_embedder.py#L26): We use CLIP to match the embeddings, which match the format of our DB embeddings
- [Embedding Retrieval](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/search.py#L120): Retrieves embeddings using ANN search
- [Text Match Retrieval](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/search.py#L134): Match titles
- [De-dupe and Merge](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/search.py#L153): Combine similarity scores for items retrieved in both, and deduplicate results.
- [Re-rank](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/search.py#L173C9-L173C25): Items were re-ranked - for example, results with more+higher rankings were boosted. Re-ranking rules/logic [here](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/search.py#L6-L25).

## Data Pipeline

![data pipeline diagram](data_pipeline.png)

- [Token Classifier](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/data_processing/parse_titles.ipynb): First I batch processed and grabbed all the unique tokens from all the text + descriptions + features. I passed the top 2000 of them into gpt-4o-mini and had it classify them by gender / category / color / style. I was then able to apply these hardcoded mappings to be scrappy classifier that extracted tokens and classified by gender / category / color / style.
- [Format Text For Embedding](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/data_processing/parse_titles.ipynb): In the same notebook, about 75% down the page, see the function `format_product` that provides the `text_for_embedding` column. This function formats the text in a standard way, ready to be embedded
- [Create Product Schema](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/models.py): This product schema was created for a postgres table with a pgvector-backed Embedding column
- [Insert Metadata into table](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/scripts/upsert.py): First, all the Products were inserted into the metadata table.
- [Upsert Embeddings](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/api/app/scripts/upsert_embeddings.py): Next, the embeddings were created using CLIP and upserted - a more expensive operation.

## Other Experiments / Scripts

- Initial data explorations [notebook](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/data_processing/exploration.ipynb) to determine primary keys (title + ASIN), sparsity of price data, etc.
- Played with some [image captioning](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/data_processing/images.ipynb) models to experiment with extracting insights from images. Also experimented with FashionCLIP, but decided that the text data was sufficient for this use case.
- [Script to convert JSONL to JSON](https://github.com/zhang-lucy/openai-fashion-assistant/blob/main/data_processing/convert_to_json.py)

## Next Steps

- Fuzzy matching on token classifier in data pipeline
- Image embeddings
- More standard text embeddings
- Separate embeddings table
- Run both retrieval methods in parallel (text + embeddings) to improve performance
- Collect user behavior data to be able to train a model to do proper retrieval
