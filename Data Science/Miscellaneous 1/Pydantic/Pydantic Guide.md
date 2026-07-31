Absolutely, Jack — here’s your **refined and complete Pydantic guide**, integrating everything:  
✅ model structure, defaults, nested & list models, validation, computed fields, serialization, and inheritance — all in **clean, professional format** for practical reference.

---

# ⚙️ **Pydantic — Complete Practical Reference**

---

## **1️⃣ Basic Model**

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

user1 = User(id=1, name="Jack", email="jack@example.com")
print(user1)
```

**Output:**

```
id=1 name='Jack' email='jack@example.com'
```

---

## **2️⃣ Default Values**

```python
class Product(BaseModel):
    name: str
    price: float = 0.0
    in_stock: bool = True

p = Product(name="Laptop")
print(p)
```

**Output:**

```
name='Laptop' price=0.0 in_stock=True
```

---

## **3️⃣ Field Validation**

```python
from pydantic import BaseModel, Field

class Employee(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2)
    salary: float = Field(..., ge=1000)
```

---

## **4️⃣ Nested Models**

```python
class Address(BaseModel):
    city: str
    zipcode: str

class Person(BaseModel):
    name: str
    age: int
    address: Address

person = Person(
    name="Jack",
    age=25,
    address={"city": "Chennai", "zipcode": "600001"}
)
print(person)
```

---

## **5️⃣ Lists of Models**

```python
class Item(BaseModel):
    name: str
    price: float

class Order(BaseModel):
    id: int
    items: list[Item]

order = Order(
    id=101,
    items=[{"name": "Laptop", "price": 1200}, {"name": "Mouse", "price": 20}]
)
print(order)
```

---

## **6️⃣ Optional Fields**

```python
from typing import Optional

class Book(BaseModel):
    title: str
    author: Optional[str] = None
```

---

## **7️⃣ Convert to Dict or JSON**

```python
user = User(id=2, name="Alice", email="alice@example.com")
print(user.model_dump())         # dict
print(user.model_dump_json())    # JSON string
```

---

## **8️⃣ Field-Level Validation — `@field_validator`**

```python
from pydantic import field_validator

class Student(BaseModel):
    name: str
    age: int

    @field_validator("name")
    def must_be_title_case(cls, v):
        if not v.istitle():
            raise ValueError("Name must be in title case")
        return v

    @field_validator("age")
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Age must be positive")
        return v

student = Student(name="Jack", age=22)
print(student)
```

---

## **9️⃣ Model-Level Validation — `@model_validator`**

```python
from pydantic import model_validator

class Course(BaseModel):
    name: str
    duration_months: int
    price: float

    @model_validator(mode="after")
    def validate_course(self):
        if self.duration_months > 6 and self.price < 1000:
            raise ValueError("Courses longer than 6 months must cost at least 1000.")
        return self

Course(name="ML Bootcamp", duration_months=3, price=800)
```

---

## **🔟 Computed Fields — `@computed_field`**

```python
from pydantic import computed_field

class Rectangle(BaseModel):
    length: float
    width: float

    @computed_field
    @property
    def area(self) -> float:
        return self.length * self.width

rect = Rectangle(length=10, width=5)
print(rect.area)
print(rect.model_dump())
```

**Output:**

```
50.0
{'length': 10.0, 'width': 5.0, 'area': 50.0}
```

---

## **1️⃣1️⃣ Serialization Examples**

```python
from datetime import datetime

class Log(BaseModel):
    message: str
    timestamp: datetime

log = Log(message="Task completed", timestamp=datetime.now())

print(log.model_dump())        # Python dict
print(log.model_dump_json())   # JSON string
```

---

## **1️⃣2️⃣ Model Inheritance**

You can extend models just like in OOP — all validations and fields are inherited.

```python
class BaseUser(BaseModel):
    id: int
    name: str

class AdvancedUser(BaseUser):
    email: str
    role: str = "user"

user = AdvancedUser(id=1, name="Jack", email="jack@example.com")
print(user)
```

**Output:**

```
id=1 name='Jack' email='jack@example.com' role='user'
```

> 🔁 All fields and validators from the parent class are automatically available in the child model.

---

## **1️⃣3️⃣ Complete Example — Combined Usage**

```python
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Optional

class UserProfile(BaseModel):
    name: str
    email: str
    age: int = Field(..., gt=0)
    country: Optional[str] = "India"
    purchases: int = 0

    @field_validator("email")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @model_validator(mode="after")
    def check_age_and_purchases(self):
        if self.age < 18 and self.purchases > 0:
            raise ValueError("Underage users cannot make purchases")
        return self

    @computed_field
    @property
    def is_adult(self) -> bool:
        return self.age >= 18

class PremiumUser(UserProfile):
    membership_level: str = "Gold"

user = PremiumUser(name="Jack", email="jack@example.com", age=21, purchases=3)
print(user.model_dump_json(indent=2))
```

**Output:**

```json
{
  "name": "Jack",
  "email": "jack@example.com",
  "age": 21,
  "country": "India",
  "purchases": 3,
  "is_adult": true,
  "membership_level": "Gold"
}
```

---

### ✅ **Summary**

|Feature|Decorator / Method|Purpose|
|---|---|---|
|`Field()`|Define constraints and metadata|Field-level configuration|
|`@field_validator`|Validate or modify individual fields|Input validation|
|`@model_validator`|Validate relationships between fields|Cross-field logic|
|`@computed_field`|Create read-only calculated fields|Derived properties|
|`.model_dump()`|Convert model to dictionary|Internal use|
|`.model_dump_json()`|Convert model to JSON|External serialization|
|Inheritance|Extend base models|Reusable structures|

---

Would you like me to also show a **short real-world use case** (for instance, validating an API user-order payload using nested inheritance)? It’s a great way to visualize how these parts work together in production code.