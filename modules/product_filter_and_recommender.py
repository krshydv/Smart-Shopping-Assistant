import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def parse_delivery_time(delivery_str):
    parts = delivery_str.split()
    if len(parts) >= 1:
        range_part = parts[0]
        if '-' in range_part:
            try:
                min_str, max_str = range_part.split('-')
                return int(min_str), int(max_str)
            except:
                return None, None
        else:
            try:
                days = int(range_part)
                return days, days
            except:
                return None, None
    return None, None


def filter_products(data, min_price=None, max_price=None, min_rating=None, min_reviews=None, max_delivery_days=None):
    filtered = []
    for p in data:
        if min_price is not None and p['price'] < min_price:
            continue
        if max_price is not None and p['price'] > max_price:
            continue
        if min_rating is not None and p['seller_rating'] < min_rating:
            continue
        if min_reviews is not None and p['review_count'] < min_reviews:
            continue
        if max_delivery_days is not None:
            min_d, max_d = parse_delivery_time(p['delivery_time'])
            if max_d is not None and max_d > max_delivery_days:
                continue
        filtered.append(p)
    return filtered


def build_feature_matrix(data):
    brands = sorted({p.get('brand', '') for p in data if p.get('brand')})
    ram_vals = []
    prices = []
    for p in data:
        try:
            ram_num = int(''.join(filter(str.isdigit, p.get('RAM', ''))))
        except:
            ram_num = 0
        ram_vals.append(ram_num)
        prices.append(p.get('price', 0))
    ram_min, ram_max = min(ram_vals), max(ram_vals)
    price_min, price_max = min(prices), max(prices)
    X = []
    for p in data:
        brand_vec = [0] * len(brands)
        if p['brand'] in brands:
            brand_vec[brands.index(p['brand'])] = 1
        try:
            ram = int(''.join(filter(str.isdigit, p.get('RAM', ''))))
        except:
            ram = 0
        ram_norm = (ram - ram_min) / (ram_max - ram_min) if ram_max > ram_min else 0
        price = p.get('price', 0)
        price_norm = (price - price_min) / (price_max - price_min) if price_max > price_min else 0
        feature_vec = brand_vec + [ram_norm, price_norm]
        X.append(feature_vec)
    return np.array(X), brands, ram_min, ram_max, price_min, price_max


def recommend_products(data, user_pref, top_n=5):
    # Step 1: Strict filter
    filtered = data

    if 'brand' in user_pref:
        preferred_brands = [b.lower() for b in user_pref['brand']] if isinstance(user_pref['brand'], list) else [user_pref['brand'].lower()]
        filtered = [p for p in filtered if p.get('brand', '').lower() in preferred_brands]

    if 'RAM' in user_pref:
        target_ram = str(user_pref['RAM'])
        filtered = [p for p in filtered if target_ram in p.get('RAM', '')]

    # If nothing remains after filtering, return empty
    if not filtered:
        return []

    # Step 2: Vector-based similarity within filtered group
    X, brands, ram_min, ram_max, price_min, price_max = build_feature_matrix(filtered)

    # Build input vector
    brand_vec = [0] * len(brands)
    if 'brand' in user_pref:
        for i, b in enumerate(brands):
            if b.lower() in preferred_brands:
                brand_vec[i] = 1

    ram_norm = (int(user_pref['RAM']) - ram_min) / (ram_max - ram_min) if 'RAM' in user_pref and ram_max > ram_min else 0
    price_norm = 0
    user_vec = np.array(brand_vec + [ram_norm, price_norm]).reshape(1, -1)

    if np.count_nonzero(user_vec) == 0:
        return filtered[:top_n]

    sims = cosine_similarity(user_vec, X).flatten()
    top_indices = sims.argsort()[::-1][:top_n]
    return [filtered[i] for i in top_indices]
