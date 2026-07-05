from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import uvicorn
import stocks
import threading
import json
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import asyncio

app = FastAPI(title="Stock Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

def handle_stock_updated(data):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast(json.dumps(data)))
        else:
            asyncio.run(manager.broadcast(json.dumps(data)))
    except Exception as e:
        print("WS Broadcast error:", e)

stocks.on_stock_updated = handle_stock_updated

def scheduled_refresh():
    stocks.refresh_all_stocks()

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))
scheduler.add_job(scheduled_refresh, 'cron', hour=9, minute=0)
scheduler.start()

app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.on_event("startup")
def startup_event():
    threading.Thread(target=stocks.init_cache, daemon=True).start()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/stocks")
def get_stocks() -> List[Dict[str, Any]]:
    return stocks.get_all_stocks()

@app.get("/stock/{ticker}")
def get_stock(ticker: str) -> Dict[str, Any]:
    return stocks.get_stock_data(ticker)

@app.post("/refresh")
def refresh_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(stocks.refresh_all_stocks)
    return {"message": "Refresh started in background"}

@app.get("/search")
def search_stock(query: str):
    import search
    return search.search_ticker(query)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
