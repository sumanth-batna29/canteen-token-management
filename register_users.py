import requests
import json

def register_user(name, email, password, role):
    url = "http://localhost:8000/auth/register"
    data = {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "phone_no": "1234567890",
        "gender": "Other",
        "address": "Test Address"
    }
    try:
        response = requests.post(url, json=data)
        print(f"Registering {email}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error registering {email}: {e}")

if __name__ == "__main__":
    register_user("Admin", "admin@canteen.com", "admin", "Admin")
    register_user("Customer", "user@test.com", "password", "Customer")
