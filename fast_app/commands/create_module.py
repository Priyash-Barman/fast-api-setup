import sys
import os
import shutil
import re
from fast_app.commands.utils import (
    snake_to_pascal, 
    snake_to_kebab, 
    snake_to_words, 
    register_module, 
    print_registration_checklist
)

MODULES_DIR = "fast_app/modules"
BASE_MODULE = "demo"

IGNORE_DIRS = {"__pycache__"}
IGNORE_EXTENSIONS = {".pyc"}


# ----------------------------
# Content replacement (DEFINITIVE)
# ----------------------------
def replace_patterns(text: str, singular: str, plural: str) -> str:
    s_pascal = snake_to_pascal(singular)
    p_pascal = snake_to_pascal(plural)
    s_kebab = snake_to_kebab(singular)
    p_kebab = snake_to_kebab(plural)
    p_words = snake_to_words(plural)

    replacements = [
        (r"\bManage demos", f"Manage {p_words.lower()}"),
        
        # -------------------------------------------------
        # ROUTES
        # -------------------------------------------------
        (r'prefix="/admin/demos"', f'prefix="/admin/{p_kebab}"'),
        (r'prefix="/demos"', f'prefix="/{p_kebab}"'),
        (r'href="/admin/demos', f'href="/admin/{p_kebab}'),
        (r'url="/admin/demos', f'url="/admin/{p_kebab}'),
        
        # -------------------------------------------------
        # MODULE PATHS
        # -------------------------------------------------
        (r"\.modules\.demo\.", rf".modules.{singular}."),

        # -------------------------------------------------
        # FILE / MODULE IDENTIFIERS
        # -------------------------------------------------
        (r"\bdemo_model\b", f"{singular}_model"),
        (r"\bdemo_schema\b", f"{singular}_schema"),
        (r"\bdemo_service\b", f"{singular}_service"),
        (r"\bdemo_api\b", f"{singular}_api"),
        (r"\bdemo_web\b", f"{singular}_web"),
        (r"\bdemo_queries\b", f"{singular}_queries"),
        (r"\bdemo_mutations\b", f"{singular}_mutations"),
        (r"\bdemo_types\b", f"{singular}_types"),

        # -------------------------------------------------
        # PLURAL FUNCTIONS
        # -------------------------------------------------
        (r"\bget_demos\b", f"get_{plural}"),
        (r"\blist_demos\b", f"list_{plural}"),

        # -------------------------------------------------
        # SINGULAR FUNCTIONS
        # -------------------------------------------------
        (r"\bget_demo_by_id\b", f"get_{singular}_by_id"),
        (r"\bget_demo\b", f"get_{singular}"),
        (r"\bcreate_demo\b", f"create_{singular}"),
        (r"\bupdate_demo\b", f"update_{singular}"),
        (r"\bremove_demo\b", f"remove_{singular}"),
        (r"\bchange_demo_status\b", f"change_{singular}_status"),
        (r"\btoggle_demo_status\b", f"toggle_{singular}_status"),
        (r"\bdemos_data\b", f"{plural}_data"),

        # -------------------------------------------------
        # SNAKE_CASE IDENTIFIERS
        # -------------------------------------------------
        (r"demo_", f"{singular}_"),
        (r"_demo", f"_{singular}"),
        (r"democms_", f"{singular}_"),
        (r"_democms", f"_{singular}"),
        (r"demoform_", f"{singular}_"),
        (r"_demoform", f"_{singular}"),

        # -------------------------------------------------
        # STANDALONE identifiers
        # -------------------------------------------------
        (r"\bdemo\b", singular),
        (r"\bdemos\b", plural),
        (r"\bdemocms\b", singular),
        (r"\bdemoform\b", singular),

        # -------------------------------------------------
        # ROUTES
        # -------------------------------------------------
        (r'/demos', f'/{p_kebab}'),
        (r'/democms', f'/{p_kebab}'),
        (r'/demoform', f'/{p_kebab}'),

        # -------------------------------------------------
        # PASCAL CASE
        # -------------------------------------------------
        (r"Demo", s_pascal),
        (r"Demos", p_pascal),
        (r"Democms", s_pascal),
        (r"Demoform", s_pascal),
        (r"DemoForm", s_pascal),

        # -------------------------------------------------
        # kebab-case
        # -------------------------------------------------
        (r"\bdemo-([a-z0-9\-]+)", rf"{s_kebab}-\1"),

        # -------------------------------------------------
        # UI
        # -------------------------------------------------
        (r"\bDEMOS\b", p_words),
        
        # -------------------------------------------------
        # ROUTE NAME STRINGS (CRITICAL)
        # -------------------------------------------------
        (r'admin_demos', f'admin_{plural}'),
        (r'api_demos', f'api_{plural}'),
    ]

    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)

    return text


# ----------------------------
# Filename replacement
# ----------------------------
def rename_filename(filename: str, singular: str, plural: str) -> str:
    filename = filename.replace("demos", plural)
    filename = filename.replace("demo", singular)
    filename = filename.replace("Demo", snake_to_pascal(singular))
    return filename


# ----------------------------
# Main
# ----------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <singular> [plural]")
        sys.exit(1)

    singular = sys.argv[1]
    plural = sys.argv[2] if len(sys.argv) > 2 else singular + "s"

    src_dir = os.path.join(MODULES_DIR, BASE_MODULE)
    dest_dir = os.path.join(MODULES_DIR, singular)

    if not os.path.isdir(src_dir):
        print(f"❌ Base {BASE_MODULE} module not found")
        sys.exit(1)

    if os.path.exists(dest_dir):
        print(f"❌ Module '{singular}' already exists at {dest_dir}")
        sys.exit(1)

    # Copy files
    shutil.copytree(
        src_dir,
        dest_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    # Replace content and rename files
    for root, dirs, files in os.walk(dest_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if os.path.splitext(file)[1] in IGNORE_EXTENSIONS:
                continue

            old_path = os.path.join(root, file)
            new_name = rename_filename(file, singular, plural)
            new_path = os.path.join(root, new_name)

            with open(old_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            content = replace_patterns(content, singular, plural)

            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)

            if old_path != new_path:
                os.remove(old_path)

    # Auto-registration
    try:
        register_module(singular, plural)
        print(f"✅ Module '{singular}' created and registered successfully")
    except Exception as e:
        print(f"⚠️  Module created but auto-registration failed: {e}")
        print_registration_checklist(singular)


if __name__ == "__main__":
    main()
