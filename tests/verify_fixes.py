import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_cors():
    print("Testing CORS...")
    # Preflight request
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    if "access-control-allow-origin" not in response.headers:
        print(f"Headers: {response.headers}")
    assert response.headers["access-control-allow-origin"] == "*"
    assert response.headers["access-control-allow-methods"] == "*"
    print("CORS OK")


def test_system_options():
    print("Testing /system/options...")
    response = client.get("/system/options")
    assert response.status_code == 200
    data = response.json()
    assert "subjects" in data
    assert "grades" in data
    assert "worksheet_types" in data
    assert "statuses" in data
    print("/system/options OK")


if __name__ == "__main__":
    try:
        test_cors()
        test_system_options()
        print("\nAll verification checks passed!")
    except AssertionError as e:
        print(f"\nVerification FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
