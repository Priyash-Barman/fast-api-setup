import os
import re

def snake_to_pascal(name: str) -> str:
    return "".join(word.capitalize() for word in name.split("_"))

def snake_to_kebab(name: str) -> str:
    return name.replace("_", "-")

def snake_to_words(name: str) -> str:
    return name.replace("_", " ").upper()

def snake_to_title(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split("_"))

def register_module(singular: str, plural: str):
    s_pascal = snake_to_pascal(singular)
    
    # 1. Register in fast_app/modules/__init__.py
    init_path = "fast_app/modules/__init__.py"
    if os.path.exists(init_path):
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add to import block (handles trailing comma or not)
        if f"    {singular}," not in content and f"    {singular}\n" not in content:
            content = re.sub(r',?(\s*\n\))', rf',\n    {singular}\1', content)
            
        # Add to app_modules list
        if f"    {singular}," not in content:
            # Match with or without spaces around =
            content = re.sub(r'(app_modules\s*=\s*\[.*?)(\n\])', rf'\1\n    {singular},\2', content, flags=re.DOTALL)
            
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 2. Register in fast_app/db/models.py
    models_path = "fast_app/db/models.py"
    if os.path.exists(models_path):
        with open(models_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        import_line = f"from fast_app.modules.{singular}.models.{singular}_model import {s_pascal}"
        if import_line not in content:
            lines = content.splitlines()
            last_import_idx = 0
            for i, line in enumerate(lines):
                if i < len(lines)-1 and line.startswith("from"):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, import_line)
            content = "\n".join(lines)
            
        # Add to document_models list
        if f"    {s_pascal}," not in content:
            content = re.sub(r'(document_models\s*=\s*\[.*?)(\n\])', rf'\1\n    {s_pascal},\2', content, flags=re.DOTALL)
            
        with open(models_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 3. Register in fast_app/graphql/query.py
    query_path = "fast_app/graphql/query.py"
    if os.path.exists(query_path):
        with open(query_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        import_line = f"from fast_app.modules.{singular}.graphql.{singular}_queries import {s_pascal}Query"
        if import_line not in content:
            lines = content.splitlines()
            lines.insert(1, import_line)
            content = "\n".join(lines)
            
        # Add to Query class inheritance
        if f"    {s_pascal}Query," not in content:
            content = re.sub(r'(class Query\(.*?)(\n\):)', rf'\1\n    {s_pascal}Query,\2', content, flags=re.DOTALL)
            
        with open(query_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 4. Register in fast_app/graphql/mutation.py
    mutation_path = "fast_app/graphql/mutation.py"
    if os.path.exists(mutation_path):
        with open(mutation_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        import_line = f"from fast_app.modules.{singular}.graphql.{singular}_mutations import {s_pascal}Mutation"
        if import_line not in content:
            lines = content.splitlines()
            lines.insert(1, import_line)
            content = "\n".join(lines)
            
        # Add to Mutation class inheritance
        if f"    {s_pascal}Mutation," not in content:
            content = re.sub(r'(class Mutation\(.*?)(\n\):)', rf'\1\n    {s_pascal}Mutation,\2', content, flags=re.DOTALL)
            
        with open(mutation_path, "w", encoding="utf-8") as f:
            f.write(content)

def unregister_module(singular: str):
    s_pascal = snake_to_pascal(singular)
    
    # 1. Unregister from fast_app/modules/__init__.py
    init_path = "fast_app/modules/__init__.py"
    if os.path.exists(init_path):
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remove from import block
        content = re.sub(rf'(\n\s*{singular},)', '', content)
        # Handle case if it's the last element without a trailing comma (though we usually have one)
        content = re.sub(rf'(\n\s*{singular})', '', content)
        
        # Remove from app_modules list
        content = re.sub(rf'(\n\s*{singular},)', '', content)
        
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 2. Unregister from fast_app/db/models.py
    models_path = "fast_app/db/models.py"
    if os.path.exists(models_path):
        with open(models_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remove import line
        content = re.sub(rf'from fast_app.modules.{singular}.models.{singular}_model import {s_pascal}\n?', '', content)
        
        # Remove from document_models list
        content = re.sub(rf'(\n\s*{s_pascal},)', '', content)
        
        with open(models_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 3. Unregister from fast_app/graphql/query.py
    query_path = "fast_app/graphql/query.py"
    if os.path.exists(query_path):
        with open(query_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove import line
        content = re.sub(rf'from fast_app.modules.{singular}.graphql.{singular}_queries import {s_pascal}Query\n?', '', content)
        
        # Remove from Query class inheritance
        content = re.sub(rf'(\n\s*{s_pascal}Query,)', '', content)
        
        with open(query_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 4. Unregister from fast_app/graphql/mutation.py
    mutation_path = "fast_app/graphql/mutation.py"
    if os.path.exists(mutation_path):
        with open(mutation_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remove import line
        content = re.sub(rf'from fast_app.modules.{singular}.graphql.{singular}_mutations import {s_pascal}Mutation\n?', '', content)
        
        # Remove from Mutation class inheritance
        content = re.sub(rf'(\n\s*{s_pascal}Mutation,)', '', content)
        
        with open(mutation_path, "w", encoding="utf-8") as f:
            f.write(content)

def print_registration_checklist(singular: str):
    print("\nNext steps (Manual registration check):")
    print(f"1. Register in fast_app/modules/__init__.py")
    print(f"2. Register in fast_app/db/models.py")
    print(f"3. Register in fast_app/graphql/query.py")
    print(f"4. Register in fast_app/graphql/mutation.py")
