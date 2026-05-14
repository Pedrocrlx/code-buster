from fastapi import FastAPI

app = FastAPI(title="Code Buster API")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
