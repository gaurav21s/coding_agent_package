To implement this using the latest version of `pydantic` (v2.x), we use the `BaseModel` class. Pydantic v2 provides robust methods like `model_dump()` and `model_dump_json()` to handle serialization, replacing the deprecated `dict()` and `json()` methods from v1.

The following program defines the `Order` model, performs the requested operations, and prints the results.

```python
from pydantic import BaseModel
import json

# Define the Order model using Pydantic v2
class Order(BaseModel):
    id: int
    items: list[str]
    total: float

def main():
    # 1. Build one Order from a Python dict
    order_dict_data = {"id": 1, "items": ["apple", "banana"], "total": 10.5}
    order1 = Order(**order_dict_data)

    # 2. Build another Order from a JSON string
    order_json_data = '{"id": 2, "items": ["laptop", "mouse"], "total": 1200.0}'
    order2 = Order.model_validate_json(order_json_data)

    # 3. Make a copy of the first order with total changed to 99.5
    # model_copy allows updating fields during the copy process
    order1_copy = order1.model_copy(update={"total": 99.5})

    # 4. Print the copy as a Python dict
    print("Copy as Python dict:")
    print(order1_copy.model_dump())

    # 5. Print the copy as a JSON string
    print("\nCopy as JSON string:")
    print(order1_copy.model_dump_json())

if __name__ == "__main__":
    main()
```