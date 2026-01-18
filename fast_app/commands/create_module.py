import sys
import os
import shutil
import re

MODULES_DIR = "fast_app/modules"
BASE_MODULE = "demo"

IGNORE_DIRS = {"__pycache__"}
IGNORE_EXTENSIONS = {".pyc"}


# ----------------------------
# Name helpers
# ----------------------------
def snake_to_pascal(name: str) -> str:
    return "".join(word.capitalize() for word in name.split("_"))


def snake_to_kebab(name: str) -> str:
    return name.replace("_", "-")


def snake_to_words(name: str) -> str:
    return name.replace("_", " ").upper()


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
        # Handle prefix="/admin/demos" pattern
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

        # -------------------------------------------------
        # PLURAL FUNCTIONS (CRITICAL FIX)
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

        # -------------------------------------------------
        # SNAKE_CASE IDENTIFIERS
        # -------------------------------------------------
        (r"\bdemo_", f"{singular}_"),
        (r"_demo\b", f"_{singular}"),

        # -------------------------------------------------
        # STANDALONE demo variable
        # -------------------------------------------------
        (r"\bdemo\b", singular),

        # -------------------------------------------------
        # PLURAL WORDS
        # -------------------------------------------------
        (r"\bdemos\b", plural),

        # -------------------------------------------------
        # ROUTES
        # -------------------------------------------------
        (r"/demos\b", f"/{p_kebab}"),

        # -------------------------------------------------
        # PASCAL CASE
        # -------------------------------------------------
        (r"\bDemo([A-Z][a-zA-Z0-9]*)", rf"{s_pascal}\1"),
        (r"\bDemo\b", s_pascal),
        (r"\bDemos\b", p_pascal),

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
        print("❌ Base demo module not found")
        sys.exit(1)

    if os.path.exists(dest_dir):
        print("❌ Module already exists")
        sys.exit(1)

    shutil.copytree(
        src_dir,
        dest_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

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

    print(f"✅ Module '{singular}' created successfully")


if __name__ == "__main__":
    main()
