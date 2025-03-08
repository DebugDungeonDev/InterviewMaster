import sys
import io
import traceback

def run_code(code: str) -> str:
    """
    Executes the given code string and returns the output (stdout) or
    a traceback (with line numbers) if an exception occurs.

    Note: This version doesn't worry about security. It just compiles and executes the code.
    """
    old_stdout = sys.stdout
    new_stdout = io.StringIO()

    try:
        # Capture stdout
        sys.stdout = new_stdout
        
        # First compile the code to catch syntax errors with line numbers
        compiled_code = compile(code, "<user_code>", "exec")
        
        # Execute the compiled code in a fresh dictionary
        exec(compiled_code, {})
    except Exception:
        # Return the full traceback (including line numbers)
        error_trace = traceback.format_exc()
        return error_trace
    finally:
        # Always restore stdout
        sys.stdout = old_stdout

    # If everything runs fine, return what was printed
    return new_stdout.getvalue()
