from typing import Any
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
    ValidationError,
)

class User(BaseModel):
    # Configure model to forbid extra fields and strip whitespace from strings
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True
    )

    name: str
    email: str
    age: int

    # Field validator to reject negative ages
    @field_validator('age')
    @classmethod
    def check_age_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Age must be non-negative')
        return v

    # Field validator to lowercase the email
    @field_validator('email', mode='before')
    @classmethod
    def lowercase_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.lower()
        return v

    # Model-level check that name and email are not identical
    @model_validator(mode='after')
    def check_name_email_not_identical(self) -> 'User':
        if self.name.lower() == self.email.lower():
            raise ValueError('Name and email cannot be identical')
        return self

def main():
    # 1. Good input
    try:
        user = User(name=' Alice ', email='Alice@Example.com', age=30)
        print("Good User:")
        print(user)
    except ValidationError as e:
        print(e)

    print("\n" + "-"*20 + "\n")

    # 2. Bad input (negative age, identical name/email, extra field)
    try:
        User(name='Bob', email='bob', age=-5, extra_field='invalid')
    except ValidationError as e:
        print("Validation Error for bad input:")
        print(e)

if __name__ == '__main__':
    main()
