from fastapi import FastAPI

from app.routers import auth, task, user

app = FastAPI()


@app.get("/")
async def welcome() -> dict:
    return {"message": "My e-commerce app"}


app.include_router(task.router)
app.include_router(user.router)
app.include_router(auth.router)
