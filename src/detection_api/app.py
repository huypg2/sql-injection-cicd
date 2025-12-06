from fastapi import FastAPI
from routes import predict, health
from prometheus_client import make_asgi_app

app = FastAPI(title="SQL Injection Detector")

# Mount routes
app.include_router(health.router)
app.include_router(predict.router)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)