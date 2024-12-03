# python2proto

**python2proto** is a Python library that converts Python data models into Protocol Buffer (Protobuf) schemas. It supports various Python data models, including:

- [Pydantic](https://pydantic-docs.helpmanual.io/) models
- [Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Attrs](https://www.attrs.org/en/stable/) classes
- [TypedDict](https://docs.python.org/3/library/typing.html#typeddict)
- Regular Python classes

This tool is useful for automatically generating Protobuf schemas from existing Python code, facilitating integration with gRPC services or other systems that use Protobuf.

## Features

- **Automatic Conversion**: Converts Python data models to Protobuf message definitions.
- **Support for Collections**: Handles lists, dictionaries (maps), and optional fields.
- **Nested Models**: Recursively parses nested models and resolves circular references.
- **Type Mapping**: Maps Python types to appropriate Protobuf scalar types.

## Installation

You can install **python2proto** via `pip`:

```bash
pip install python2proto
```

## Usage

Here's an example demonstrating how to use **python2proto** to convert various Python models into Protobuf schemas.

```python:examples/simple_example.py
# examples/simple_example.py
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

# Regular Class
class RegularClass:
    class_var = 'class variable'

    def __init__(self):
        self.instance_var = 'instance variable'
        self.count = 10

    def method(self):
        pass

# Generate Protobuf schema
proto_schema = pydantic_models_to_protos([User, Product, Company, Config, TreeNode, RegularClass])
print(proto_schema)
```

### Output

The above code will generate the following Protobuf schema:

```protobuf
message RegularClass {
    string class_var = 1;
    string instance_var = 2;
    int32 count = 3;
}
message TreeNode {
    int32 value = 1;
    repeated TreeNode children = 2;
}
message Config {
    int32 version = 1;
    repeated string features = 2;
}
message Company {
    string name = 1;
    repeated User employees = 2;
}
message Product {
    int32 product_id = 1;
    string name = 2;
    float price = 3;
    repeated string tags = 4;
}
message Address {
    string street = 1;
    string city = 2;
    int32 zipcode = 3;
}
message User {
    int32 id = 1;
    string name = 2;
    bool is_active = 3;
    repeated Address addresses = 4;
    map<string, string> metadata = 5;
    map<string, string> settings = 6;
}
```

## API Reference

The core functionality is provided by the `pydantic_models_to_protos` function.

```python:python2proto/__init__.py
def pydantic_models_to_protos(models: List[Type], already_visited: Optional[Set[Type]] = None) -> str:
    """
    Converts a list of models to a Protobuf schema string.

    Args:
        models: List of model classes to convert.
        already_visited: Set of models that have already been visited to avoid circular references.

    Returns:
        A string containing the Protobuf schema definition.
    """
    # Initialize empty list for proto messages
    proto_messages = []
    
    # Initialize visited models set if not provided
    visited_models = already_visited or set()

    # Helper function to parse a single model
    def parse_model(model, message_name):
        # Skip if already visited
        if model in visited_models:
            return
        visited_models.add(model)

        # Parse fields
        fields = []
        type_hints = get_model_fields(model)
        idx = 1
        
        # Process each field
        for field_name, field_type in type_hints.items():
            # Handle Optional, List, Dict types
            # Map Python types to Proto types
            # Build field definitions
            fields.append(field_def)
            idx += 1
            
        # Build message definition
        message = f"message {message_name} {{\n"
        message += field_defs
        message += "}}\n"
        proto_messages.append(message)

    # Process each model
    for model in models:
        parse_model(model, model.__name__)

    # Join messages in reverse order
    proto_schema = '\n'.join(reversed(proto_messages))
    return proto_schema
    """
```

### Parameters

- `models`: A list of Python model classes to be converted into Protobuf messages.
- `already_visited`: (Optional) A set used internally to track already processed models, preventing infinite recursion with circular references.

### Returns

- A string containing the Protobuf schema definitions for the provided models.

## Supported Python Models

### Pydantic Models

Pydantic models are fully supported. All fields with type annotations are converted to Protobuf fields.

```python
class User(BaseModel):
    id: int
    name: str
    is_active: Optional[bool]
```

### Dataclasses

Fields of dataclasses with type annotations are converted similarly.

```python
@dataclass
class Product:
    product_id: int
    name: str
    price: float
```

### Attrs Classes

Attrs classes with type annotations are also supported.

```python
@attr.s
class Company:
    name: str = attr.ib()
    employees: List[User] = attr.ib(factory=list)
```

### TypedDict

TypedDict types are converted by processing their annotated fields.

```python
class Config(TypedDict):
    version: int
    features: List[str]
```

### Regular Python Classes

Regular classes that are not built-in types and have annotated instance variables are processed as well.

```python
class RegularClass:
    class_var = 'class variable'

    def __init__(self):
        self.instance_var = 'instance variable'
        self.count = 10
```

## Handling Collections and Maps

The library correctly handles common collection types:

- `List[T]` becomes `repeated T` in Protobuf.
- `Dict[K, V]` becomes `map<K, V>` in Protobuf.

## Recursive Models

Models that reference themselves (recursive models) are supported.

```python
@dataclass
class TreeNode:
    value: int
    children: Optional[List['TreeNode']] = None
```

## Limitations

- The type mapping is basic. Custom or complex types default to `string` in the Protobuf schema.
- Enums, oneof fields, and other advanced Protobuf features are not automatically inferred.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue on GitHub.

## License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2024 PP Autonomous

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
