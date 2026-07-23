import subprocess


def run_command(command: list[str], timeout_seconds: int = 60) -> tuple[bool, str]:
    """
    Run a shell command safely and return:
    - success status
    - combined output
    """

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )

        output = ""

        if result.stdout:
            output += result.stdout

        if result.stderr:
            output += "\n" + result.stderr

        return result.returncode == 0, output.strip()

    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout_seconds} seconds"

    except Exception as error:
        return False, f"Command failed: {str(error)}"