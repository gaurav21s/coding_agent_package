from pydantic import BaseModel
import json

                                          
class Order(BaseModel):
    id: int
    items: list[str]
    total: float

def main():
                                           
    order_dict_data = {"id": 1, "items": ["apple", "banana"], "total": 10.5}
    order1 = Order(**order_dict_data)

                                               
    order_json_data = '{"id": 2, "items": ["laptop", "mouse"], "total": 1200.0}'
    order2 = Order.model_validate_json(order_json_data)

                                                                  
                                                               
    order1_copy = order1.model_copy(update={"total": 99.5})

                                        
    print("Copy as Python dict:")
    print(order1_copy.model_dump())

                                        
    print("\nCopy as JSON string:")
    print(order1_copy.model_dump_json())

if __name__ == "__main__":
    main()
