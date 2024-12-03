from collections.abc import Set
from typing import (
    get_type_hints,
    Type,
    Optional,
    List,
    Union,
    Dict,
    Any,
    TypedDict,
)

from pydantic import BaseModel
import dataclasses
import attr
import inspect

def is_pydantic_model(cls):
    return isinstance(cls, type) and issubclass(cls, BaseModel)

def is_dataclass(cls):
    return dataclasses.is_dataclass(cls)

def is_attrs_class(cls):
    return attr.has(cls)

def is_typed_dict(cls):
    return isinstance(cls, type) and cls.__class__.__name__ == 'TypedDictMeta'

def is_regular_class(cls):
    return (
        isinstance(cls, type) and
        cls.__module__ != 'builtins' and  # Exclude built-in types
        not (
            is_pydantic_model(cls) or
            is_dataclass(cls) or
            is_attrs_class(cls) or
            is_typed_dict(cls)
        )
    )

def is_model(cls):
    # Exclude scalar types explicitly
    if cls in (int, float, str, bool, bytes, Any):
        return False
    return (
        is_pydantic_model(cls) or
        is_dataclass(cls) or
        is_attrs_class(cls) or
        is_typed_dict(cls) or
        is_regular_class(cls)
    )

def get_model_fields(model):
    if is_pydantic_model(model):
        return get_type_hints(model)
    elif is_dataclass(model):
        return {field.name: field.type for field in dataclasses.fields(model)}
    elif is_attrs_class(model):
        return {field.name: field.type for field in attr.fields(model)}
    elif is_typed_dict(model):
        return model.__annotations__
    elif is_regular_class(model):
        # Use inspect to get instance attributes
        attributes = inspect.getmembers(model, lambda a: not(inspect.isroutine(a)))
        return {name: type(value) for name, value in attributes if not(name.startswith('__') and name.endswith('__'))}
    else:
        return {}

def map_scalar_type(py_type: Type) -> str:
    type_mapping = {
        int: 'int32',
        float: 'float',
        str: 'string',
        bool: 'bool',
        bytes: 'bytes',
        Any: 'string',
    }
    return type_mapping.get(py_type, 'string')  # Default to 'string' if type not mapped

def map_type(py_type: Type) -> str:
    if py_type in (int, float, str, bool, bytes, Any):
        return map_scalar_type(py_type)
    elif is_model(py_type):
        return py_type.__name__
    else:
        # Default to 'string' for unknown types
        return 'string'

def pydantic_models_to_protos(models: List[Type], already_visited: Optional[Set[Type]] = None) -> str:
    """
    Converts a list of models to a Protobuf schema string.
    Args:
        models: List of model classes to convert.
        already_visited: Set of models that have already been visited to avoid circular references.
    Returns:
        A string containing the Protobuf schema definition.
    """
    proto_messages = []
    visited_models = already_visited or set()

    def parse_model(model: Type, message_name: str) -> None:
        if model in visited_models:
            return
        visited_models.add(model)

        fields = []
        type_hints = get_model_fields(model)
        idx = 1
        for field_name, field_type in type_hints.items():
            repeated = False
            optional = False

            # Handle Optional types
            if getattr(field_type, '__origin__', None) is Union:
                args = field_type.__args__
                if type(None) in args:
                    optional = True
                    args = tuple(arg for arg in args if arg is not type(None))
                    field_type = args[0] if args else Any

            # Handle List types
            elif getattr(field_type, '__origin__', None) in (list, List):
                repeated = True
                field_type = field_type.__args__[0]

            # Handle Dict types (maps)
            elif getattr(field_type, '__origin__', None) in (dict, Dict):
                key_type, value_type = field_type.__args__ if field_type.__args__ else (Any, Any)
                # Use 'string' as default key and value types if unspecified
                key_type_name = map_scalar_type(key_type) if key_type in (int, float, str, bool) else 'string'
                if is_model(value_type):
                    parse_model(value_type, value_type.__name__)
                    value_type_name = value_type.__name__
                else:
                    value_type_name = map_type(value_type)
                field_line = f"map<{key_type_name}, {value_type_name}> {field_name} = {idx};"
                fields.append(field_line)
                idx += 1
                continue

            # Recursively parse nested models
            if is_model(field_type):
                parse_model(field_type, field_type.__name__)
                field_type_name = field_type.__name__
            else:
                field_type_name = map_type(field_type)

            field_rule = 'repeated' if repeated else ''
            field_line = f"{field_rule} {field_type_name} {field_name} = {idx};".strip()
            fields.append(field_line)
            idx += 1

        # Build the message definition
        message = f"message {message_name} {{\n"
        for field in fields:
            message += f"    {field};\n"
        message += "}\n"
        proto_messages.append(message)

    for model in models:
        parse_model(model, model.__name__)

    proto_schema = '\n'.join(reversed(proto_messages))
    return proto_schema 