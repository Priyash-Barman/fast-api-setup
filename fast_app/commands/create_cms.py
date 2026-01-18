import sys
import os
import shutil
import re

MODULES_DIR = "fast_app/modules"
BASE_MODULE = "democms"

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

def snake_to_title(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split("_"))



# ----------------------------
# Content replacement (DEFINITIVE)
# ----------------------------
def replace_patterns(text: str, singular: str, plural: str) -> str:
    s_pascal = snake_to_pascal(singular)
    p_pascal = snake_to_pascal(plural)
    s_kebab = snake_to_kebab(singular)
    p_kebab = snake_to_kebab(plural)
    p_words = snake_to_words(plural)
    p_title = snake_to_title(singular)

    replacements = [
        (r"\bManage CMS", f"Manage {p_words.lower()}"),
        (r'tags=\["Manage Democms"\]', f'tags=["Manage {p_title}"]'),
        (r'tags=\["Democms"\]', f'tags=["{p_title}"]'),
        (r"\bManage CMS", f"Manage {p_words.lower()}"),
        
        # -------------------------------------------------
        # ROUTES
        # -------------------------------------------------
        # Handle prefix="/admin/democmss" pattern
        (r'prefix="/admin/democms"', f'prefix="/admin/{p_kebab}"'),
        (r'prefix="/democms"', f'prefix="/{p_kebab}"'),
        (r'href="/admin/democms', f'href="/admin/{p_kebab}'),
        (r'url="/admin/democms', f'url="/admin/{p_kebab}'),
        (r'url="/democms', f'url="/{p_kebab}'),
        
        # -------------------------------------------------
        # MODULE PATHS
        # -------------------------------------------------
        (r"\.modules\.democms\.", rf".modules.{singular}."),

        # -------------------------------------------------
        # FILE / MODULE IDENTIFIERS
        # -------------------------------------------------
        (r"manage_democms", f"manage_{singular}"),
        (r"\bdemocms_model\b", f"{singular}_model"),
        (r"\bdemocms_schema\b", f"{singular}_schema"),
        (r"\bdemocms_service\b", f"{singular}_service"),
        (r"\bdemocms_api\b", f"{singular}_api"),
        (r"\bdemocms_web\b", f"{singular}_web"),

        # -------------------------------------------------
        # PLURAL FUNCTIONS (CRITICAL FIX)
        # -------------------------------------------------
        (r"\bget_democms\b", f"get_{plural}"),
        (r"\blist_democms\b", f"list_{plural}"),

        # -------------------------------------------------
        # SINGULAR FUNCTIONS
        # -------------------------------------------------
        (r"\bget_democms_by_id\b", f"get_{singular}_by_id"),
        (r"\bget_democms\b", f"get_{singular}"),
        (r"\bcreate_democms\b", f"create_{singular}"),
        (r"\bupdate_democms\b", f"update_{singular}"),
        (r"\bremove_democms\b", f"remove_{singular}"),
        (r"\bchange_democms_status\b", f"change_{singular}_status"),

        # -------------------------------------------------
        # SNAKE_CASE IDENTIFIERS
        # -------------------------------------------------
        (r"\bdemocms_", f"{singular}_"),
        (r"_democms\b", f"_{singular}"),

        # -------------------------------------------------
        # STANDALONE democms variable
        # -------------------------------------------------
        (r"\bdemocms\b", singular),

        # -------------------------------------------------
        # PLURAL WORDS
        # -------------------------------------------------
        (r"\bdemocms\b", plural),

        # -------------------------------------------------
        # ROUTES
        # -------------------------------------------------
        (r"/democms\b", f"/{p_kebab}"),

        # -------------------------------------------------
        # PASCAL CASE
        # -------------------------------------------------
        (r"\bDemocms([A-Z][a-zA-Z0-9]*)", rf"{s_pascal}\1"),
        (r"\bDemocms\b", s_pascal),

        # -------------------------------------------------
        # kebab-case
        # -------------------------------------------------
        (r"\bdemocms-([a-z0-9\-]+)", rf"{s_kebab}-\1"),

        # -------------------------------------------------
        # UI
        # -------------------------------------------------
        (r"\bDEMOCMS\b", p_words),
        
        # -------------------------------------------------
        # ROUTE NAME STRINGS (CRITICAL)
        # -------------------------------------------------
        (r'admin_democms', f'admin_{plural}'),
        (r'api_democms', f'api_{plural}'),
    ]
    
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)

    return text


# ----------------------------
# Filename replacement
# ----------------------------
def rename_filename(filename: str, singular: str, plural: str) -> str:
    filename = filename.replace("democmss", plural)
    filename = filename.replace("democms", singular)
    filename = filename.replace("Democms", snake_to_pascal(singular))
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
        print("❌ Base democms module not found")
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
