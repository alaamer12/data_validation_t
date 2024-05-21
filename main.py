from functools import wraps
from dataclasses import dataclass, field
from pydantic import BaseModel, EmailStr, PositiveInt, ValidationError, validator, field_validator
from marshmallow import Schema, fields, validate, validates_schema, ValidationError as MarshmallowValidationError
import attr
import re
from typing import Optional


def type_check(follows: Optional[str] = None, *types):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not all(isinstance(arg, typ) for arg, typ in zip(args, types)):
                raise TypeError("Arguments must match specified types")
            if not follows or not re.match(follows, func.__name__):
                raise ValueError("Function name must match follows pattern")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Dataclass
@dataclass
class PersonWithDataclass:
    name: str
    age: int = field(default=0)
    email: str = field(default='')

    def __post_init__(self):
        if not self.name:
            raise ValueError("name must not be empty")

    def __str__(self):
        return f"{self.name} {self.age} {self.email}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name} {self.age} {self.email})"


# Pydantic
class PersonWithPydantic(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("name must not be empty")
        return v

    def __str__(self):
        return f"{self.name} {self.age} {self.email}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name} {self.age} {self.email})"


# Marshmallow
class PersonWithMarshmallow(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    age = fields.Integer(required=True)
    email = fields.Email(required=True)

    @validates_schema
    def validate_age(self, data, **kwargs):
        if data["age"] <= 0:
            raise MarshmallowValidationError("age must be positive")

    def __str__(self):
        return f"{self.name} {self.age} {self.email}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name} {self.age} {self.email})"


# attrs
@attr.s
class PersonWithAttrs:
    name = attr.ib(type=str)
    age = attr.ib(type=int, default=0)
    email = attr.ib(type=str, default='')

    @name.validator
    def validate_name(self, attribute, value):
        if not value:
            raise ValueError("name must not be empty")

    def __str__(self):
        return f"{self.name} {self.age} {self.email}"


if __name__ == '__main__':
    person_with_dataclass = PersonWithDataclass(name="John", age=30, email="X7Q9u@example.com")
    print(person_with_dataclass)
    person_with_attrs = PersonWithAttrs(name="John", age=30, email="X7Q9u@example.com")
    print(person_with_attrs)
    person_with_marshmallow = PersonWithMarshmallow().load({"name": "John", "age": 30, "email": "X7Q9u@example.com"})
    print(person_with_marshmallow)
    person_with_pydantic = PersonWithPydantic(name="John", age=30, email="X7Q9u@example.com")
    print(person_with_pydantic)
