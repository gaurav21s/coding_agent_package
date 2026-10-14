from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict, ValidationError

class User(BaseModel):
    # Configure model: forbid extra fields, strip whitespace from strings
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True
    )

    name: str
    email: str
    age: int

    # Per-field validator: lowercase the email
    @field_validator('email')
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()

    # Per-field validator: reject negative ages
    @field_validator('age')
    @classmethod
    def check_positive_age(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Age cannot be negative')
        return v

    # Model-level check: name and email are not identical
    @model_validator(mode='after')
    def check_name_not_email(self) -> 'User':
        if self.name.lower() == self.email.lower():
            raise ValueError('Name and email cannot be identical')
        return self

def main():
    # 1. Good input
    good_data = {
        "name": " Alice ",
        "email": "ALICE@Example.com",
        "age": 30
    }
    
    print("--- Validating Good Input ---")
    try:
        user = User(**good_data)
        print(f"Success: {user}")
    except ValidationError as e:
        print(e)

    # 2. Bad input (Negative age and identical name/email)
    bad_data = {
        "name": "bob",
        "email": "bob",
        "age": -5
    }

    print("\n--- Validating Bad Input ---")
    try:
        User(**bad_data)
    except ValidationError as e:
        print(f"Caught expected validation error:\n{e}")

if __name__ == "__main__":
    main()
