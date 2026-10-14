import contextlib
from fastapi import FastAPI
from fastapi.testclient import TestClient

                   
model = {}

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
                             
    print("--- Startup: Loading model ---")
    model["factor"] = 2
    yield
                               
    print("--- Shutdown: Clearing model ---")
    model.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict")
async def predict(x: int):
    factor = model.get("factor", 1)
    return {"result": x * factor}

def run_test():
                                                                
    with TestClient(app) as client:
        response = client.get("/predict?x=3")
        print(f"Response from /predict?x=3: {response.json()}")

if __name__ == "__main__":
    run_test()
