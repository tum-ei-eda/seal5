from dataclasses import dataclass
from dacite import from_dict, Config


@dataclass
class User:
    name: str
    age: int
    is_active: bool


data = {
    'name': 'John',
    'age': 30,
    'is_active': True,
    "foo": "bar",
}

user = from_dict(data_class=User, data=data, config=Config(strict=True))

print("user", user)

assert user == User(name='John', age=30, is_active=True)
