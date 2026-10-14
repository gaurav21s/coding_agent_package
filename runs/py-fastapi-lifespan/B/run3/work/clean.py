import contextlib
from fastapi import FastAPI
from fastapi.testclient import TestClient

                                   
model = {}

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
                             
    print("Application starting up: Loading model...")
    model["factor"] = 2
    yield
                               
    print("Application shutting down: Clearing model...")
    model.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict")
def predict(x: int):
                             
    factor = model.get("factor", 0)
    return {"result": x * factor}

def run_test():
                                                                        
    with TestClient(app) as client:
        print("Testing /predict?x=3...")
        response = client.get("/predict?x=3")
        print(f"Response JSON: {response.json()}")

if __name__ == "__main__":
    run_test()
