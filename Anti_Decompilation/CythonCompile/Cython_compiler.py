# Cython_compiler.py
# Extract from exe: https://github.com/extremecoders-re/pyinstxtractor
# Decompiler for pyc: https://pylingual.io
# Core files for testing: Cython_compiler.py, setup.py (Dynamically generated), browse_annoying_site.py (Testing input file)
import sys
import os
import shutil
import subprocess
from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension
import PyInstaller.__main__
import glob
import re


def parse_imports(script_path):
    """
    Parse the target Python script to find all import statements.
    Returns a list of modules to include in PyInstaller's `--hidden-import`.
    """
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to match import statements
    import_pattern = r'^\s*(?:import\s+([\w_]+)|from\s+([\w_]+)\s+import)'
    matches = re.findall(import_pattern, content, re.MULTILINE)

    # Extract module names
    modules = set()
    for match in matches:
        modules.update(filter(None, match))

    return list(modules)


def compile_with_cython(target_script):
    """
    Compiles the given Python script into a Cython-compiled shared object (.pyd/.so).
    """
    base_name = os.path.splitext(os.path.basename(target_script))[0]
    compiled_name = f"{base_name}_cython_compiled"
    print(f"Compiling {target_script} with Cython...")

    setup_content = f"""
from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

ext_modules = [
    Extension("{compiled_name}", ["{target_script}"])
]

setup(
    name="{compiled_name}",
    ext_modules=cythonize(ext_modules, compiler_directives={{'language_level': "3"}}),
    zip_safe=False,
)
"""

    setup_file = 'setup.py'
    with open(setup_file, 'w') as f:
        f.write(setup_content)

    try:
        subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during Cython compilation: {e}")
        return False

    os.remove(setup_file)

    # Locate and rename compiled output
    if sys.platform == "win32":
        pattern = f"{compiled_name}*.pyd"
        new_compiled_file = f"{compiled_name}.pyd"
    else:
        pattern = f"{compiled_name}*.so"
        new_compiled_file = f"{compiled_name}.so"

    compiled_files = glob.glob(pattern)
    if compiled_files:
        compiled_file = compiled_files[0]
        os.rename(compiled_file, new_compiled_file)
        print(f"Compiled {compiled_file} to {new_compiled_file}")
    else:
        print("Compiled module not found.")
        return False

    try:
        os.remove(f"{base_name}.c")
    except FileNotFoundError:
        pass

    return compiled_name


def create_executable(compiled_module_name, hidden_imports):
    """
    Creates an executable file from the compiled Cython module using PyInstaller.
    """
    wrapper_script = f"""
import {compiled_module_name}

if __name__ == '__main__':
    {compiled_module_name}.main()
"""
    wrapper_script_name = "wrapper_script.py"
    with open(wrapper_script_name, 'w') as f:
        f.write(wrapper_script)

    try:
        # Add hidden imports to PyInstaller arguments
        hidden_import_args = []
        for imp in hidden_imports:
            hidden_import_args.extend(['--hidden-import', imp])

        PyInstaller.__main__.run([
            '--onefile',
            '--clean',
            '--name', compiled_module_name,
            *hidden_import_args,
            wrapper_script_name,
        ])
    except Exception as e:
        print(f"Error during PyInstaller execution: {e}")
        return False

    executable_name = f"{compiled_module_name}.exe" if sys.platform == "win32" else compiled_module_name
    dist_path = os.path.join('dist', executable_name)
    target_path = os.path.join('Output', executable_name)

    if os.path.exists(dist_path):
        os.makedirs("Output", exist_ok=True)
        shutil.move(dist_path, target_path)
        print(f"Executable created: {target_path}")
    else:
        print("Executable not found.")
        return False

    os.remove(wrapper_script_name)
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree(f'{compiled_module_name}.egg-info', ignore_errors=True)
    try:
        os.remove(f"{compiled_module_name}.pyd")
        os.remove(f"{compiled_module_name}.spec")
    except FileNotFoundError:
        pass

    return target_path


def cython_compilation(target_script):
    """
    Compiles the given Python script into a Cython module and creates an executable.
    """
    if not os.path.isfile(target_script):
        print(f"Error: {target_script} does not exist.")
        return False, "Target script does not exist."

    # Parse imports from the target script
    hidden_imports = parse_imports(target_script)
    print(f"Hidden imports detected: {hidden_imports}")

    compiled_module_name = compile_with_cython(target_script)
    if not compiled_module_name:
        return False, "Failed to compile with Cython."

    target_path = create_executable(compiled_module_name, hidden_imports)
    if not target_path:
        return False, "Failed to create executable."

    return True, target_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python Cython_compiler.py <path_to_python_script>")
        sys.exit(1)

    target_script = sys.argv[1]
    success, message = cython_compilation(target_script)

    if success:
        print(f"Compilation and executable creation successful: {message}")
    else:
        print(f"Error: {message}")


if __name__ == '__main__':
    main()
