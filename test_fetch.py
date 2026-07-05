import indicators
import json

res = indicators.fetch_and_calculate("RELIANCE.NS")
print(json.dumps(res, indent=2))
