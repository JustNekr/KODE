import uvicorn
from fastapi import FastAPI
from auth.views import router as auth_router
from notes.views import router as notes_router

app = FastAPI(title="KODE", docs_url="/")

app.include_router(auth_router)
app.include_router(notes_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
