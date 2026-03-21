import json
import urllib.request

def postcode_to_latlon(postcode: str):
    """
    Convert a UK postcode into (latitude, longitude) using postcodes.io.

    Returns:
        (lat, lon) as floats, or (None, None) if lookup fails.
    """
    if not postcode:
        return None, None

    clean = postcode.strip().upper().replace(" ", "")

    try:
        url = f"https://api.postcodes.io/postcodes/{clean}"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())

        if data.get("status") == 200:
            result = data["result"]
            return result["latitude"], result["longitude"]

    except Exception:
        # Any network or parsing error → fail gracefully
        return None, None

    return None, None
