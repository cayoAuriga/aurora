from fastapi import FastAPI
# el cliente de FastAPI :D
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}