import sys
import os
import shutil
from fast_app.commands.utils import unregister_module

MODULES_DIR = "fast_app/modules"

def main():
    if len(sys.argv) < 2:
        print("Usage: python fast_app/commands/remove_module.py <singular>")
        sys.exit(1)

    singular = sys.argv[1]
    dest_dir = os.path.join(MODULES_DIR, singular)

    if not os.path.exists(dest_dir):
        print(f"❌ Module '{singular}' does not exist at {dest_dir}")
        sys.exit(1)

    confirm = input(f"Are you sure you want to delete module '{singular}' and all its files? (y/N): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)

    # 1. Unregister
    try:
        unregister_module(singular)
        print(f"✅ Module '{singular}' unregistered successfully")
    except Exception as e:
        print(f"⚠️  Unregistration failed: {e}")

    # 2. Delete files
    try:
        shutil.rmtree(dest_dir)
        print(f"✅ Module directory '{dest_dir}' deleted successfully")
    except Exception as e:
        print(f"❌ Failed to delete directory: {e}")

    print(f"\n✅ Module '{singular}' removed successfully.")

if __name__ == "__main__":
    main()
