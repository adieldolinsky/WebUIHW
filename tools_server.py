"""Local Flask tools server.

Exposes two GET endpoints:
  - /exchange_rate    : convert a price from INR to a target currency
  - /similar_product  : find the top 3 similar products on Amazon via RapidAPI

API keys are loaded from a .env file using python-dotenv. Never hardcode keys.
"""

import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

EXCHANGE_RATE_URL = "https://api.exchangerate-api.com/v4/latest/INR"
AMAZON_SEARCH_URL = "https://real-time-amazon-data.p.rapidapi.com/search"
RAPIDAPI_HOST = "real-time-amazon-data.p.rapidapi.com"

# Network timeout (seconds) for all outbound requests.
REQUEST_TIMEOUT = 10

@app.route("/", methods=["GET"])
def health_check():
    """Root endpoint to verify the server is running."""
    return jsonify({"status": "running", "message": "Tools server is active."}), 200


@app.route("/exchange_rate", methods=["GET"])
def exchange_rate():
    """Convert `price` (INR) into `target_currency`."""
    price_raw = request.args.get("price")
    target_currency = request.args.get("target_currency")

    if price_raw is None or target_currency is None:
        return (
            jsonify({"error": "Missing required query parameters: 'price' and 'target_currency'."}),
            400,
        )

    try:
        # Strip everything except digits and the decimal point
        clean_price_str = re.sub(r'[^\d.]', '', price_raw)
        
        if not clean_price_str:
            return jsonify({"error": "No valid numeric digits found in 'price'."}), 400
            
        price = float(clean_price_str)
    except (TypeError, ValueError):
        return jsonify({"error": "'price' must contain a valid number."}), 400
    target_currency = target_currency.strip().upper()

    try:
        response = requests.get(EXCHANGE_RATE_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        return (
            jsonify({"error": "Failed to fetch exchange rates.", "details": str(exc)}),
            502,
        )

    try:
        data = response.json()
    except ValueError:
        return jsonify({"error": "Invalid response from exchange rate service."}), 502

    rates = data.get("rates", {})
    rate = rates.get(target_currency)

    if rate is None:
        return (
            jsonify({"error": f"Unsupported or unknown target currency: '{target_currency}'."}),
            400,
        )

    converted_price = round(price * rate, 4)

    return jsonify(
        {
            "base_currency": "INR",
            "target_currency": target_currency,
            "original_price": price,
            "exchange_rate": rate,
            "converted_price": converted_price,
        }
    )


@app.route("/similar_product", methods=["GET"])
def similar_product():
    """Return the top 3 similar Amazon products for `product_name`."""
    product_name = request.args.get("product_name")

    if not product_name or not product_name.strip():
        return jsonify({"error": "Missing required query parameter: 'product_name'."}), 400

    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return (
            jsonify({"error": "Server is missing the RAPIDAPI_KEY environment variable."}),
            500,
        )

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }
    params = {"query": product_name.strip()}

    try:
        response = requests.get(
            AMAZON_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        return (
            jsonify({"error": "Failed to fetch similar products.", "details": str(exc)}),
            502,
        )

    try:
        data = response.json()
    except ValueError:
        return jsonify({"error": "Invalid response from product search service."}), 502

    products = data.get("data", {}).get("products", [])

    top_products = []
    for product in products[:3]:
        top_products.append(
            {
                "title": product.get("product_title"),
                "price": product.get("product_price"),
                "url": product.get("product_url"),
            }
        )

    return jsonify(
        {
            "product_name": product_name.strip(),
            "count": len(top_products),
            "similar_products": top_products,
        }
    )


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found."}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
