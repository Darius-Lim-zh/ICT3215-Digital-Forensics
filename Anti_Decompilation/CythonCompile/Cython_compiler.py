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
import sys

from sympy import false


def compile_with_cython(target_script):
    # Remove extension from filename
    base_name = os.path.splitext(os.path.basename(target_script))[0]
    compiled_name = f"{base_name}_cython_compiled"
    print(compiled_name)

    # Dynamically create setup.py content
    setup_content = f"""
from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

# Define the extension module for Cython
ext_modules = [
    Extension("{compiled_name}", ["{target_script}"])
]

# Setup configuration for building the Cython extension
setup(
    name="{compiled_name}",
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={{'language_level': "3"}}
    ),
    zip_safe=False,
)
"""

    # Write the setup.py file to the current directory
    setup_file = 'setup.py'
    with open(setup_file, 'w') as f:
        f.write(setup_content)

    # Run the dynamically generated setup.py to compile with CythonCompile
    try:
        subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during Cython compilation: {e}")
        # sys.exit(1)
        return False

    # Cleanup generated setup.py after compilation
    os.remove(setup_file)

    # # Define the extension module
    # extensions = [Extension(compiled_name, [target_script])]
    #
    # # Compile the extension module
    # setup(
    #     name=compiled_name,
    #     ext_modules=cythonize(
    #         extensions,
    #         compiler_directives={'language_level': "3"},
    #     ),
    #     script_args=['build_ext', '--inplace'],
    # )

    # Used to ensure that only the compiled name remains
    # Find the compiled module with suffixes
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
        print(f"Renamed {compiled_file} to {new_compiled_file}")
    else:
        print("Compiled module not found.")
        # sys.exit(1)
        return False

    # Remove unnecessary files
    try:
        os.remove(f'{base_name}.c')
        os.remove(f'{compiled_name}.c')
    except FileNotFoundError:
        pass

def create_executable(compiled_module_name):
    # Create a temporary Python script that imports and runs the compiled module
    wrapper_script = f"""
import {compiled_module_name}

if __name__ == '__main__':
    {compiled_module_name}.main()
"""
    wrapper_script_name = 'wrapper_script.py'
    with open(wrapper_script_name, 'w') as f:
        f.write(wrapper_script)

    # Use PyInstaller to create the executable
    try:
        PyInstaller.__main__.run([
            '--onefile',
            '--clean',
            '--name', compiled_module_name,
            wrapper_script_name,
        ])
    except Exception as e:
        print(f"Error during PyInstaller execution: {e}")
        # sys.exit(1)
        return False

    # Determine the executable name
    if sys.platform == "win32":
        executable_name = f"{compiled_module_name}.exe"
    else:
        executable_name = compiled_module_name  # No extension on Unix-like systems

    # Move the executable to current directory
    dist_path = os.path.join('dist', executable_name)
    target_path = os.path.join('..', '..', 'Output', executable_name)

    print(dist_path)
    if os.path.exists(dist_path):
        # shutil.move(dist_path, f'./{executable_name}')
        shutil.move(dist_path, target_path)
        # print(f"Executable created: ./{executable_name}")
        print(f"Executable created: {target_path}")
    else:
        print("Executable not found.")
        print(f"Available files: {os.listdir('dist')}")
        # sys.exit(1)
        return False

    # Cleanup
    os.remove(wrapper_script_name)
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree(f'{compiled_module_name}.egg-info', ignore_errors=True)
    try:
        os.remove(f'{compiled_module_name}.pyd')
        os.remove(f'{compiled_module_name}.spec')
    except FileNotFoundError:
        pass

    return target_path

# To be used in the UI
def cython_compilation(target_script):
    if not os.path.isfile(target_script):
        print(f"Error: {target_script} does not exist.")
        # sys.exit(1)
        return False

    compile_with_cython(target_script)

    base_name = os.path.splitext(os.path.basename(target_script))[0]
    compiled_module_name = f"{base_name}_cython_compiled"

    # Created the executable that has been compiled with
    target_path = create_executable(compiled_module_name)

    return target_path

def main():
    if len(sys.argv) != 2:
        print("Usage: python Cython_compiler.py <path_to_python_script>")
        sys.exit(1)

    target_script = sys.argv[1]
    if not os.path.isfile(target_script):
        print(f"Error: {target_script} does not exist.")
        sys.exit(1)

    cython_compilation(target_script)
    # # Compile the target script with CythonCompile
    # compile_with_cython(target_script)
    #
    # # Get the base name of the script without extension
    # base_name = os.path.splitext(os.path.basename(target_script))[0]
    # compiled_module_name = f"{base_name}_comp"
    #
    # print(compiled_module_name)
    # # Create the executable using PyInstaller
    # create_executable(compiled_module_name)

if __name__ == '__main__':
    main()
