import json
from pydantic import BaseModel

# Define the Order model
class Order(BaseModel):
    id: int
    items: list[str]
    total: float

def main():
    # 1. Build one Order from a Python dict
    order_dict_data = {"id": 1, "items": ["apple", "banana"], "total": 10.5}
    order1 = Order(**order_dict_data)
    print(f"Order 1 (from dict): {order1}")

    # 2. Build another Order from a JSON string
    order_json_str = '{"id": 2, "items": ["orange", "grape"], "total": 20.0}'
    order2 = Order.model_validate_json(order_json_str)
    print(f"Order 2 (from JSON): {order2}")

    # 3. Make a copy of the first order with total changed to 99.5
    # model_copy allows updating fields during the copy process
    order1_copy = order1.model_copy(update={"total": 99.5})
    print(f"Order 1 Copy (modified): {order1_copy}")

    # 4. Print the copy as a Python dict
    print(f"Copy as dict: {order1_copy.model_dump()}")

    # 5. Print the copy as a JSON string
    print(f"Copy as JSON: {order1_copy.model_dump_json()}")

if __name__ == "__main__":
    main()
