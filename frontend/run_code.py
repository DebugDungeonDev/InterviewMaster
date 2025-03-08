import io
import sys

def run_code(code: str) -> str:
    # Redirect stdout to capture print statements
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        exec(code)
    except Exception as e:
        return str(e)
    finally:
        # Reset stdout
        sys.stdout = old_stdout

    # Get the captured output
    output = new_stdout.getvalue()
    return output