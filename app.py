
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/search/?q=solana"

# Market cap tier configurations
TIER_CONFIG = {
    "micro": {"min": 0, "max": 1_000_000, "volume_pct": 50, "liquidity_pct": 5},
    "small": {"min": 1_000_000, "max": 10_000_000, "volume_pct": 20, "liquidity_pct": 10},
    "mid": {"min": 10_000_000, "max": 50_000_000, "volume_pct": 10, "liquidity_pct": 15},
    "high": {"min": 50_000_000, "max": float("inf"), "volume_pct": 5, "liquidity_pct": 20},
}

def fetch_filtered_tokens(tier):
    config = TIER_CONFIG.get(tier, TIER_CONFIG["micro"])
    try:
        res = requests.get(DEXSCREENER_API)
        data = res.json().get("pairs", [])
        filtered = []

        for token in data:
            mcap = token.get("fdv") or 0
            volume_1h = token.get("volume", {}).get("h1", 0)
            liquidity = token.get("liquidity", {}).get("usd", 0)

            if not (mcap and volume_1h and liquidity):
                continue

            if not (config["min"] <= mcap < config["max"]):
                continue

            volume_ratio = (volume_1h / mcap) * 100
            liquidity_ratio = (liquidity / mcap) * 100

            if liquidity_ratio >= config["liquidity_pct"] and volume_ratio >= config["volume_pct"]:
                filtered.append({
                    "name": token.get("baseToken", {}).get("name"),
                    "symbol": token.get("baseToken", {}).get("symbol"),
                    "mcap": round(mcap, 2),
                    "liquidity": round(liquidity, 2),
                    "volume_1h": round(volume_1h, 2),
                    "volume_ratio": round(volume_ratio, 2),
                    "liquidity_ratio": round(liquidity_ratio, 2),
                    "url": token.get("url")
                })

        return filtered

    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/')
def index():
    tier = request.args.get("tier", "micro")
    tokens = fetch_filtered_tokens(tier)
    return render_template('index.html', tokens=tokens, selected_tier=tier)

if __name__ == '__main__':
    app.run(debug=True)
