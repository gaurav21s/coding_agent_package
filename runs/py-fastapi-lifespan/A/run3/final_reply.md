To implement this, we use the `lifespan` context manager, which is the modern, recommended way to handle startup and shutdown events in FastAPI (replacing the deprecated `@app.on_event` decorators).

We will use `fastapi` and `httpx` (which `TestClient` depends on). As of October 2026, these libraries maintain full compatibility with the `lifespan` pattern.

```python
import contextlib
from fastapi import FastAPI
from fastapi.testclient import TestClient

# The "model" state
model = {}

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the model
    print("--- Startup: Loading model ---")
    model["factor"] = 2
    yield
    # Shutdown: Clear the model
    print("--- Shutdown: Clearing model ---")
    model.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict")
async def predict(x: int):
    factor = model.get("factor", 1)
    return {"result": x * factor}

def run_test():
    # TestClient uses the lifespan context manager automatically
    with TestClient(app) as client:
        response = client.get("/predict?x=3")
        print(f"Response from /predict?x=3: {response.json()}")

if __name__ == "__main__":
    run_test()
```