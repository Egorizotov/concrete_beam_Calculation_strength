from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.handlers import router

app = FastAPI(
    title="ЮГ БЕТОН — каталог бетонных смесей",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
