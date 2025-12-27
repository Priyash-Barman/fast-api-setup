from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from copy import deepcopy


def customize_swagger_ui(
    app: FastAPI,
    *,
    hide_default: bool = True,
    default_tag_replacement: str | None = None,
) -> None:
    """
    Customize Swagger UI behavior.

    - Hides implicit 'default' tag from main Swagger
    - Preserves Swagger UI parameters
    - Extensible for future Swagger customizations
    """

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        paths = deepcopy(schema.get("paths", {}))
        filtered_paths: dict = {}

        for path, methods in paths.items():
            new_methods = {}

            for method, operation in methods.items():
                tags = operation.get("tags", ["default"])
                is_default = tags == ["default"]

                # Hide default routes entirely
                if hide_default and is_default:
                    continue

                # Remove default tag if mixed
                if "default" in tags:
                    tags = [t for t in tags if t != "default"]

                if not tags and default_tag_replacement:
                    operation["tags"] = [default_tag_replacement]
                elif tags:
                    operation["tags"] = tags
                else:
                    operation.pop("tags", None)

                new_methods[method] = operation

            if new_methods:
                filtered_paths[path] = new_methods

        schema["paths"] = filtered_paths
        app.openapi_schema = schema
        return schema

    # Override OpenAPI generator
    app.openapi = custom_openapi # type: ignore

    # Preserve + set Swagger UI parameters
    app.swagger_ui_parameters = {
        "docExpansion": "none",
        "filter": True,
        "showRequestDuration": True,
        "syntaxHighlight.theme": "obsidian",
        "tryItOutEnabled": True,
        "tagsSorter": "alpha",
        # "operationsSorter": "alpha",
        "defaultModelsExpandDepth": -1,
    }
