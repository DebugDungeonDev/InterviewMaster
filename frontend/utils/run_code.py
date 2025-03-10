import sys 
import io

def run_code(code: str) -> str:
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        exec(code)
    except Exception as e:
        return str(e)
    finally:
        sys.stdout = old_stdout

    return new_stdout.getvalue()