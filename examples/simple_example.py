from pydantic import BaseModel
from dataclasses import dataclass
import attr
from typing import Optional, List, Dict, Any, TypedDict

from python2proto import pydantic_models_to_protos

# Pydantic Model
class Address(BaseModel):
    street: str
    city: str
    zipcode: int

class User(BaseModel):
    id: int
    name: str
    is_active: Optional[bool]
    addresses: List[Address]
    metadata: Dict[str, Any]
    settings: Dict[str, str]

# Data Class
@dataclass
class Product:
    product_id: int
    name: str
    price: float
    tags: Optional[List[str]] = None

# Attrs Class
@attr.s
class Company:
    name: str = attr.ib()
    employees: List[User] = attr.ib(factory=list)

# TypedDict
class Config(TypedDict):
    version: int
    features: List[str]

# Recursive Data Class
@dataclass
class TreeNode:
    value: int
    children: Optional[List['TreeNode']] = None  # Recursive type

from python2proto import pydantic_models_to_protos

class RegularClass:
    class_var = 'class variable'

    def __init__(self):
        self.instance_var = 'instance variable'
        self.count = 10

    def method(self):
        pass


# Generate Protobuf schema
proto_schema = pydantic_models_to_protos([User])
print(proto_schema)

proto_schema = pydantic_models_to_protos([Product])
print(proto_schema)

proto_schema = pydantic_models_to_protos([Company])
print(proto_schema)

proto_schema = pydantic_models_to_protos([Config])
print(proto_schema)

proto_schema = pydantic_models_to_protos([TreeNode])
print(proto_schema)

proto_schema = pydantic_models_to_protos([RegularClass])
print(proto_schema)

proto_schema = pydantic_models_to_protos([Company], already_visited={User, Config})
print(proto_schema)

# Example with multiple models and circular references
proto_schema = pydantic_models_to_protos([User, Product, Company, Config, TreeNode])
print("\nMultiple models:")
print(proto_schema)

# Example with nested models
class Department(BaseModel):
    name: str
    head: User
    budget: float

class Organization(BaseModel):
    name: str
    departments: List[Department]
    config: Config

proto_schema = pydantic_models_to_protos([Organization])
print("\nNested models:")
print(proto_schema)

# Example with maps/dictionaries
class Inventory(BaseModel):
    items: Dict[str, Product]  # Map product ID to Product
    quantities: Dict[str, int] # Map product ID to quantity
    metadata: Dict[str, str]   # Generic string metadata

proto_schema = pydantic_models_to_protos([Inventory])
print("\nMaps/Dictionaries:")
print(proto_schema)

# Example with all types
class AllTypes(BaseModel):
    int_field: int
    float_field: float 
    str_field: str
    bool_field: bool
    bytes_field: bytes
    any_field: Any
    optional_str: Optional[str]
    str_list: List[str]
    model_list: List[User]
    str_dict: Dict[str, str]
    model_dict: Dict[str, Product]

proto_schema = pydantic_models_to_protos([AllTypes])
print("\nAll types:")
print(proto_schema)
