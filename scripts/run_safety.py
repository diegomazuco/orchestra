import os
import subprocess
import sys
import tempfile


def run_safety() -> None:
    """Executa a verificação de segurança do Safety em um ambiente uv."""
    try:
        # Generate pip freeze output to a temporary file
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_reqs_file:
            subprocess.run(
                ["uv", "pip", "freeze"], check=True, stdout=temp_reqs_file, text=True
            )
            temp_reqs_file_path = temp_reqs_file.name

        # Run safety check on the temporary file
        safety_command = [
            "uv",
            "run",
            "safety",
            "check",
            "--full-report",
            f"--file={temp_reqs_file_path}",
        ]

        result = subprocess.run(
            safety_command, check=False, capture_output=True, text=True
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            sys.exit(result.returncode)

    except subprocess.CalledProcessError as e:
        print(f"Erro ao gerar uv pip freeze ou executar safety: {e}", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up the temporary file
        if "temp_reqs_file_path" in locals() and os.path.exists(temp_reqs_file_path):
            os.remove(temp_reqs_file_path)


if __name__ == "__main__":
    run_safety()
