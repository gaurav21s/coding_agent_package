import json
from pydantic import BaseModel

                        
class Order(BaseModel):
    id: int
    items: list[str]
    total: float

def main():
                                           
    order_dict_data = {"id": 1, "items": ["apple", "banana"], "total": 10.5}
    order1 = Order(**order_dict_data)
    print(f"Order 1 (from dict): {order1}")

                                               
    order_json_str = '{"id": 2, "items": ["orange", "grape"], "total": 20.0}'
    order2 = Order.model_validate_json(order_json_str)
    print(f"Order 2 (from JSON): {order2}")

                                                                  
                                                               
    order1_copy = order1.model_copy(update={"total": 99.5})
    print(f"Order 1 Copy (modified): {order1_copy}")

                                        
    print(f"Copy as dict: {order1_copy.model_dump()}")

                                        
    print(f"Copy as JSON: {order1_copy.model_dump_json()}")

if __name__ == "__main__":
    main()
