# from pathlib import Path


# POLICY_DIR = Path("app/policies")


# def load_policy(policy_name: str) -> str:
#     """
#     Load a single policy file.
#     """

#     policy_path = POLICY_DIR / policy_name

#     if not policy_path.exists():
#         return ""

#     return policy_path.read_text(encoding="utf-8")


# def load_all_policies() -> str:
#     """
#     Combine all policies into one string.
#     """

#     combined = []

#     for policy_file in POLICY_DIR.glob("*.md"):
#         print(f"Loading policy: {policy_file.name}")
#         combined.append(
#             policy_file.read_text(encoding="utf-8")
#         )

#     return "\n\n".join(combined)


# print(load_all_policies())

from pathlib import Path


class PolicyService:
    """
    Loads governance policy documents.
    """

    def __init__(self):

        self.policy_dir = (
            Path(__file__).parent.parent
            / "policies"
        )

    def load_policies(self) -> dict[str, str]:
        """
        Read every markdown file.
        """

        policies = {}

        for file in self.policy_dir.glob("*.md"):

            policies[file.stem] = file.read_text(
                encoding="utf-8"
            )

        return policies