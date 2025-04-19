
from flask import Flask, render_template
import requests

app = Flask(__name__)

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/pairs/solana"

def fetch_filtered_tokens():
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

            volume_ratio = (volume_1h / mcap) * 100
            liquidity_ratio = (liquidity / mcap) * 100

            if liquidity_ratio >= 10 and volume_ratio >= 20:
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
    tokens = fetch_filtered_tokens()
    return render_template('index.html', tokens=tokens)

if __name__ == '__main__':
    app.run(debug=True)
