from fastapi import FastAPI

app = FastAPI(
    title="STARCORE Platform",
    version="0.1.0-dev",
)


@app.get("/")
def root():
    return {
        "project": "STARCORE Platform",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
