import py_compile
import os

def compile_with_cython(input_file, output_file):
    if not output_file.endswith(".pyc"):
        output_file += ".pyc"

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        # Use `cfile` to set the compiled file output location
        py_compile.compile(input_file, cfile=output_file)
        return output_file
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
