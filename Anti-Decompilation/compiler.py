# compiler.py

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

def compile_with_cython(target_script):
    # Remove extension from filename
    base_name = os.path.splitext(os.path.basename(target_script))[0] + "_comp"
    compiled_name = f"{base_name}_comp"

    # Define the extension module
    extensions = [Extension(base_name, [target_script])]

    # Compile the extension module
    setup(
        name=base_name,
        ext_modules=cythonize(
            extensions,
            compiler_directives={'language_level': "3"},
        ),
        script_args=['build_ext', '--inplace'],
    )

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
    PyInstaller.__main__.run([
        '--onefile',
        '--clean',
        '--name', compiled_module_name,
        wrapper_script_name,
    ])

    # Move the executable to current directory
    dist_path = os.path.join('dist', compiled_module_name)
    print(dist_path)
    if os.path.exists(dist_path):
        shutil.move(dist_path, f'./{compiled_module_name}.exe')
        print(f"Executable created: ./{compiled_module_name}.exe")
    else:
        print("Executable not found.")

    # Cleanup
    # os.remove(wrapper_script_name)
    # shutil.rmtree('build', ignore_errors=True)
    # shutil.rmtree('dist', ignore_errors=True)
    # shutil.rmtree(f'{compiled_module_name}.egg-info', ignore_errors=True)
    # try:
    #     os.remove(f'{compiled_module_name}.c')
    #     os.remove(f'{compiled_module_name}.pyd')
    #     os.remove(f'{compiled_module_name}.spec')
    # except FileNotFoundError:
    #     pass

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <path_to_python_script>")
        sys.exit(1)

    target_script = sys.argv[1]
    if not os.path.isfile(target_script):
        print(f"Error: {target_script} does not exist.")
        sys.exit(1)

    # Compile the target script with Cython
    compile_with_cython(target_script)

    # Get the base name of the script without extension
    base_name = os.path.splitext(os.path.basename(target_script))[0]
    compiled_module_name = f"{base_name}_comp"

    print(compiled_module_name)
    # Create the executable using PyInstaller
    create_executable(compiled_module_name)

if __name__ == '__main__':
    main()
