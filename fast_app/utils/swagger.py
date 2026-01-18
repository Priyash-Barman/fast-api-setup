from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from copy import deepcopy
from typing import Iterable

hidden_tags_list=[
    "Manage demos",
    "Manage Democms",
    "Democms",
    "Manage demoforms"
]

def customize_swagger_ui(
    app: FastAPI,
    *,
    hide_tags: Iterable[str] | None = None,
    hide_default: bool = True,
    default_tag_replacement: str | None = None,
) -> None:
    """
    Customize Swagger UI behavior.

    - Hide routes that contain only hidden tags
    - Remove hidden tags from mixed-tag routes
    - Optionally replace empty tags with a default
    """

    hidden_tags = set(hide_tags or hidden_tags_list)
    if hide_default:
        hidden_tags.add("default")

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
                tags_set = set(tags)

                # 🚫 Hide route completely if all tags are hidden
                if tags_set.issubset(hidden_tags):
                    continue

                # ✂ Remove hidden tags if mixed
                visible_tags = [t for t in tags if t not in hidden_tags]

                if not visible_tags and default_tag_replacement:
                    operation["tags"] = [default_tag_replacement]
                elif visible_tags:
                    operation["tags"] = visible_tags
                else:
                    operation.pop("tags", None)

                new_methods[method] = operation

            if new_methods:
                filtered_paths[path] = new_methods

        schema["paths"] = filtered_paths
        app.openapi_schema = schema
        return schema

    # Override OpenAPI generator
    app.openapi = custom_openapi  # type: ignore

    # Swagger UI parameters
    app.swagger_ui_parameters = {
        "docExpansion": "none",
        "filter": True,
        "showRequestDuration": True,
        "syntaxHighlight.theme": "obsidian",
        "tryItOutEnabled": True,
        "tagsSorter": "alpha",
        "defaultModelsExpandDepth": -1,
    }
