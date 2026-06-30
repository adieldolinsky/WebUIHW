# Tools Server

A small local Flask server exposing two GET endpoints: currency conversion and Amazon similar-product search.

## Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
venv\Scripts\activate    # Windows PowerShell
# source venv/bin/activate  # macOS / Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file (copy from `.env.example`) and add your RapidAPI key:

```
RAPIDAPI_KEY=your_rapidapi_key_here
```

4. Run the server:

```bash
python tools_server.py
```

The server runs on `http://0.0.0.0:5005`.

## Endpoints

### `GET /exchange_rate`

Convert a price from INR to a target currency.

| Query param        | Type   | Example |
| ------------------ | ------ | ------- |
| `price`            | float  | `1000`  |
| `target_currency`  | string | `USD`   |

Example:

```bash
curl "http://localhost:5005/exchange_rate?price=1000&target_currency=USD"
```

Sample response:

```json
{
  "base_currency": "INR",
  "target_currency": "USD",
  "original_price": 1000.0,
  "exchange_rate": 0.012,
  "converted_price": 12.0
}
```

### `GET /similar_product`

Return the top 3 similar Amazon products for a search term.

| Query param    | Type   | Example      |
| -------------- | ------ | ------------ |
| `product_name` | string | `headphones` |

Example:

```bash
curl "http://localhost:5005/similar_product?product_name=headphones"
```

Sample response:

```json
{
  "product_name": "headphones",
  "count": 3,
  "similar_products": [
    { "title": "...", "price": "$19.99", "url": "https://www.amazon.com/..." }
  ]
}
```
