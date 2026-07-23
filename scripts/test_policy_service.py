from app.services.policy_service import PolicyService

service = PolicyService()

policies = service.load_policies()

for name, content in policies.items():

    print("=" * 50)
    print(name)
    print("=" * 50)
    print(content)