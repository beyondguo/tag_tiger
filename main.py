from fastapi import FastAPI
from routers import label_sys, task, document, users
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return {"message": "Hello World"}

app.include_router(label_sys.router)
app.include_router(task.router)
app.include_router(document.router)
app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run(app='main:app', host="0.0.0.0", port=9000, reload=True, debug=False)
