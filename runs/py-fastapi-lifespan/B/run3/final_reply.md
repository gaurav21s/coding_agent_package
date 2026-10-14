To build this application, we use FastAPI's `lifespan` context manager, which is the recommended way to handle startup and shutdown events. We will use `httpx` (which is a dependency of `fastapi[standard]`) for the `TestClient`.

The following program defines the `lifespan` function to initialize and clear the `model` dictionary, sets up the `/predict` endpoint, and uses `TestClient` to verify the lifecycle and functionality.

```python
import contextlib
from fastapi import FastAPI
from fastapi.testclient import TestClient

# In-memory storage for our 'model'
model = {}

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the model
    print("Application starting up: Loading model...")
    model["factor"] = 2
    yield
    # Shutdown: Clear the model
    print("Application shutting down: Clearing model...")
    model.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict")
def predict(x: int):
    # Access the model factor
    factor = model.get("factor", 0)
    return {"result": x * factor}

def run_test():
    # TestClient acts as a context manager that triggers lifespan events
    with TestClient(app) as client:
        print("Testing /predict?x=3...")
        response = client.get("/predict?x=3")
        print(f"Response JSON: {response.json()}")

if __name__ == "__main__":
    run_test()
```

### How to run:
1. Ensure you have `fastapi` and `httpx` installed:
   ```bash
   pip install fastapi httpx
   ```
2. Save the code above as `main.py`.
3. Run the script:
   ```bash
   python main.py
   ```

The output will show the startup message, the JSON response from the API, and the shutdown message, confirming that the lifecycle events were executed correctly.