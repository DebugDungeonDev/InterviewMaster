import subprocess
import tempfile
import os
import stat
import ast

# Explicitly allowed modules (whitelist)
ALLOWED_IMPORTS = {'math', 'random', 'datetime', 'time', 'collections', 'itertools'}

# Safe built-ins
SAFE_BUILTINS = {'print': print, 'range': range, 'len': len, 'abs': abs, 'min': min, 'max': max, 'sum': sum}

# AST-based validation to enforce import restrictions and built-ins safety
def is_code_safe(code: str) -> (bool, str):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax Error: {str(e)}"

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module_name = (node.module if isinstance(node, ast.ImportFrom) else node.names[0].name)
            if module_name.split('.')[0] not in ALLOWED_IMPORTS:
                return False, f"Forbidden module import detected: {module_name}"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in SAFE_BUILTINS:
                return False, f"Use of forbidden builtin function: {node.func.id}"
    return True, ""


def run_code(code: str) -> str:
    # 1. AST check for code safety
    safe, message = is_code_safe(code)
    if not safe:
        return f"Error: {message}"

    tmp_file_path = None
    try:
        # 2. Write user code to a temporary file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
            tmp_file_path = tmp_file.name
            tmp_file.write(code.encode('utf-8'))

        # Set strict permissions
        os.chmod(tmp_file_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        # 3. Docker security flags
        cmd = [
            "docker", "run", "--rm", "--network", "none",
            "--memory", "128m", "--cpus", "0.5",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--pids-limit", "64",
            "--user", "65534:65534",
            "--read-only",
            "--tmpfs", "/tmp:rw,size=64m",
            "-v", f"{tmp_file_path}:/tmp/user_code.py:ro",
            "python:3.9-slim",
            "python3", "/tmp/user_code.py"
        ]

        # 4. Run the container
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        output = result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        output = "Execution timed out."
    except Exception as e:
        output = f"Error running container: {str(e)}"
    finally:
        # Clean up temporary file
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

    return output


if __name__ == "__main__":
    # Safe test
    user_code_safe = """
print("Hello, Secure World!")
"""
    print(run_code(user_code_safe))

    # Unsafe test
    user_code_unsafe = """
import os
os.system('echo Hacked!')
"""
    print(run_code(user_code_unsafe))
