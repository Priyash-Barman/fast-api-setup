from fastapi import Form, UploadFile, File, Request, HTTPException
from typing import Any, Dict, Type, Callable, get_origin, get_args, Union, List, Optional
from pydantic import BaseModel, ValidationError, create_model
from functools import wraps
import inspect


def form_data(Model: Type[BaseModel]):
    def decorator(endpoint: Callable):
        model_fields = Model.model_fields
        modified_fields = {}

        # --------------------------------
        # Build relaxed model (skip UploadFile validation)
        # --------------------------------
        for name, field in model_fields.items():
            field_type = field.annotation
            origin = get_origin(field_type)

            is_file = False

            if field_type == UploadFile:
                is_file = True
            elif origin is list and get_args(field_type)[0] == UploadFile:
                is_file = True
            elif origin is Union:
                for arg in get_args(field_type):
                    if arg == UploadFile:
                        is_file = True
                    elif get_origin(arg) is list and get_args(arg)[0] == UploadFile:
                        is_file = True

            modified_fields[name] = (Any, field.default) if is_file else (field_type, field.default)
        
        ModifiedModel = create_model(f"Form{Model.__name__}", **modified_fields) # type: ignore

        # --------------------------------
        # Runtime wrapper
        # --------------------------------
        @wraps(endpoint)
        async def wrapper(request: Request, **form_kwargs):

            for key, value in list(form_kwargs.items()):
                if isinstance(value, list):
                    if (
                        len(value) == 1
                        and (
                            value[0] == ""
                            or (hasattr(value[0], "filename") and value[0].filename == "")
                        )
                    ):
                        form_kwargs[key] = None
                elif value == "":
                    form_kwargs[key] = None

            filtered = {
                k: v for k, v in form_kwargs.items()
                if v is not None and v is not ...
            }

            try:
                relaxed = ModifiedModel(**filtered)
            except ValidationError as e:
                raise HTTPException(status_code=422, detail=e.errors())

            data = relaxed.model_dump(exclude_none=True)

            # Restore file fields
            for key, value in form_kwargs.items():
                if isinstance(value, UploadFile):
                    data[key] = value
                elif isinstance(value, list) and all(isinstance(v, UploadFile) for v in value):
                    data[key] = value
                elif key not in data:
                    data[key] = None

            try:
                instance = Model(**data)
            except ValidationError:
                # Validate non-file fields only
                non_file_data = {
                    k: v for k, v in data.items()
                    if not isinstance(v, UploadFile)
                    and not (isinstance(v, list) and all(isinstance(i, UploadFile) for i in v))
                }
                Model(**non_file_data)

                instance = object.__new__(Model)
                for k, v in data.items():
                    setattr(instance, k, v)

            kwargs: Dict[str, Any] = {"request": request}
            for name in inspect.signature(endpoint).parameters:
                if name != "request":
                    kwargs[name] = instance
                    break

            return await endpoint(**kwargs)

        # --------------------------------
        # Swagger signature
        # --------------------------------
        parameters = [
            inspect.Parameter(
                "request",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Request,
            )
        ]

        for name, field in model_fields.items():
            field_type = field.annotation
            origin = get_origin(field_type)

            is_file = False
            is_list = False
            is_optional = False

            if origin is Union:
                args = get_args(field_type)
                if type(None) in args:
                    is_optional = True
                for arg in args:
                    if arg == UploadFile:
                        is_file = True
                    elif get_origin(arg) is list and get_args(arg)[0] == UploadFile:
                        is_file = True
                        is_list = True
            elif field_type == UploadFile:
                is_file = True
            elif origin is list and get_args(field_type)[0] == UploadFile:
                is_file = True
                is_list = True

            if is_file:
                default = File(None) if is_optional else File(...)
                annotation = List[UploadFile] if is_list else UploadFile
            else:
                default = Form(None) if is_optional else Form(...)
                annotation = field_type # type: ignore

            parameters.append(
                inspect.Parameter(
                    name,
                    inspect.Parameter.KEYWORD_ONLY,
                    default=default,
                    annotation=annotation,
                )
            )

        wrapper.__signature__ = inspect.Signature(parameters)  # type: ignore
        return wrapper

    return decorator
