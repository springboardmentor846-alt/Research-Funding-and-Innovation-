"""Quick verification: import the app and check that all routes mount."""
import sys


def main():
    try:
        from app.main import app
        routes = [r.path for r in app.routes]
        print(f"✓ App imported successfully. {len(routes)} routes registered.")
        for r in routes:
            if "/api/" in r:
                print(f"  - {r}")
        print("✓ Verification complete")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
