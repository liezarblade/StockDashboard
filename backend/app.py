from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uvicorn
import stocks

app = FastAPI(title="Stock Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Initialize cache on startup if empty
    stocks.init_cache()

@app.get("/stocks")
def get_stocks() -> List[Dict[str, Any]]:
    return stocks.get_all_stocks()

@app.get("/stock/{ticker}")
def get_stock(ticker: str) -> Dict[str, Any]:
    return stocks.get_stock_data(ticker)

@app.post("/refresh")
def refresh_data(background_tasks: BackgroundTasks):
    # Triggers a background refresh and returns immediately
    background_tasks.add_task(stocks.refresh_all_stocks)
    return {"message": "Refresh started in background"}

@app.get("/search")
def search_stock(query: str):
    import search
    return search.search_ticker(query)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
