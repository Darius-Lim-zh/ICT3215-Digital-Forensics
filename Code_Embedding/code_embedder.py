import ast
import astor
import os


def extract_functions_and_imports(filepath):
    """
    Helper function to extract imports and function definitions from an external Python file
    :param filepath:
    :return:
    """
    with open(filepath, 'r') as file:
        external_code = file.read()

    external_tree = ast.parse(external_code)

    imports = []
    functions = []

    # Iterate over the body of the external script
    for node in external_tree.body:
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            # Collect import statements
            imports.append(node)
        elif isinstance(node, ast.FunctionDef):
            # Collect function definitions
            functions.append(node)

    return imports, functions


def import_exists(new_imports, target_tree):
    """
    Function to check if the import already exists in the target script
    :param new_imports:
    :param target_tree:
    :return:
    """
    existing_imports = [node for node in target_tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]

    for new_import in new_imports:
        for existing_import in existing_imports:
            if ast.dump(existing_import) == ast.dump(new_import):
                return True
    return False


def wrap_main_with_injected_functions(tree, func_names, func_wrapped="main", loc_to_inject="main"):
    """
    This function wraps the main() function call within injected function checks.
    Depending on loc_to_inject, it injects the condition before or after main().
    If any injected function returns False, main() is not called.

    :param tree: AST of the target script.
    :param func_names: List of function names to inject.
    :param func_wrapped: The main function to wrap.
    :param loc_to_inject: "main" to inject before main(), "end" to inject after main().
    :return:
    """
    if len(func_names) == 0:
        return  # No functions to inject

    # Build the comparison: func1() and func2() and ...
    comparison = ast.BoolOp(op=ast.And(), values=[
        ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=[], keywords=[])
        for func in func_names
    ])

    if loc_to_inject == "main":
        # Construct the if statement: if not (comparison):
        new_if_stmt = ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=comparison),
            body=[
                ast.Expr(value=ast.Call(func=ast.Name(id=func_wrapped, ctx=ast.Load()), args=[], keywords=[]))
            ],
            orelse=[]
        )
    elif loc_to_inject == "end":
        # Construct the if statement: if not (comparison):
        #     pass  # Or any other action if needed
        new_if_stmt = ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=comparison),
            body=[
                # Replace 'pass' with any other function call if needed
                ast.Pass()
            ],
            orelse=[]
        )
    else:
        print(f"Invalid loc_to_inject: {loc_to_inject}. Must be 'main' or 'end'.")
        return 1

    # Find the `if __name__ == '__main__':` block
    for node in tree.body:
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare):
                # Check if the comparison is "__name__ == '__main__'"
                left = node.test.left
                comparators = node.test.comparators
                if isinstance(left, ast.Name) and left.id == '__name__':
                    if len(comparators) == 1 and isinstance(comparators[0], ast.Constant) and comparators[
                        0].value == '__main__':
                        if loc_to_inject == "main":
                            # Find the main() call
                            for idx, stmt in enumerate(node.body):
                                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                    if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "main":
                                        # Replace main() call with the conditional
                                        node.body[idx] = new_if_stmt
                                        return 0
                            # If main() not found, append the conditional at the beginning
                            node.body.insert(0, new_if_stmt)
                        elif loc_to_inject == "end":
                            # Find the main() call
                            for idx, stmt in enumerate(node.body):
                                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                    if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "main":
                                        # Insert the conditional after main() call
                                        node.body.insert(idx + 1, new_if_stmt)
                                        return 0
                            # If main() not found, append the conditional at the end
                            node.body.append(new_if_stmt)
    return 0


def append_injected_functions_before_main(tree, func_names):
    """
    This function appends the injected calls right before the main() function is called.
    :param tree:
    :param func_names:
    :return:
    """
    # Find the 'if __name__ == "__main__"' block and inject the function calls there
    for node in tree.body:
        if isinstance(node, ast.If):
            # Look for the "__main__" condition
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                    # Find the position of main() call
                    main_call_index = None
                    for idx, stmt in enumerate(node.body):
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "main":
                                main_call_index = idx
                                break
                    if main_call_index is not None:
                        # Inject the function calls before main()
                        for func in reversed(func_names):  # Reverse to maintain order
                            injected_call = ast.Expr(
                                value=ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=[], keywords=[]))
                            node.body.insert(main_call_index, injected_call)
                    else:
                        # If main() not found, inject at the beginning
                        for func in reversed(func_names):  # Reverse to maintain order
                            injected_call = ast.Expr(
                                value=ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=[], keywords=[]))
                            node.body.insert(0, injected_call)
    return 0


def append_injected_functions_after_main(tree, func_names):
    """
    This function appends the injected calls right after the main() function is called.
    :param tree:
    :param func_names:
    :return:
    """
    # Find the 'if __name__ == "__main__"' block and inject the function calls there
    for node in tree.body:
        if isinstance(node, ast.If):
            # Look for the "__main__" condition
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                    # Find the position of main() call
                    main_call_index = None
                    for idx, stmt in enumerate(node.body):
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "main":
                                main_call_index = idx
                                break
                    if main_call_index is not None:
                        # Inject the function calls after main()
                        for func in func_names:
                            injected_call = ast.Expr(
                                value=ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=[], keywords=[]))
                            node.body.insert(main_call_index + 1, injected_call)
                    else:
                        # If main() not found, inject at the end
                        for func in func_names:
                            injected_call = ast.Expr(
                                value=ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=[], keywords=[]))
                            node.body.append(injected_call)
    return 0


def embed_code(embed_code_filenames=["mal_code.py"], src_code_filename='target_script.py', loc_to_inject="main",
               func_names=["injected_function"],
               wrap=True, new_name=""):
    """
    Function will take in code to embed along with the source file and perform transformation on it depending on the
    customization done to it. It can wrap the main function with the injected code or append the injected code.
    :param embed_code_filenames: List of filenames of code to embed
    :param src_code_filename: Filename that you want to embed code into
    :param loc_to_inject: "main" or "end", location in the code where you want to put the injected function
    :param func_names: List of names of the injected functions
    :param wrap: True/False Whether you want to wrap as an if condition pre-running main() func
    :param new_name: The new name for the modified code
    :return:
    """
    try:
        # Initialize lists to hold all imports and functions to embed
        all_imports = []
        all_functions = []

        # Iterate over each embed_code_filename and extract imports and functions
        for embed_code_filename, func_name in zip(embed_code_filenames, func_names):
            imports, functions = extract_functions_and_imports(embed_code_filename)
            all_imports.extend(imports)
            all_functions.extend(functions)

        # Load and parse the target Python script
        with open(src_code_filename, 'r') as src_code:
            target_code = src_code.read()

        # Parse the target code into an AST
        target_tree = ast.parse(target_code)

        # Inject imports if they don't already exist in the target script
        # Find the insertion point after the last existing import
        injection_point = 0
        for idx, node in enumerate(target_tree.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                injection_point = idx + 1  # Insert after the last existing import

        # Check and append imports
        for new_import in all_imports:
            if not import_exists([new_import], target_tree):
                target_tree.body.insert(injection_point, new_import)
                injection_point += 1  # Increment to keep inserting imports in order

        # Inject the function definitions above the main block
        if all_functions:
            # Insert all function definitions right after the imports
            target_tree.body[injection_point:injection_point] = all_functions

        # Inject function calls based on wrap and loc_to_inject
        if func_names:
            if wrap:
                wrap_main_with_injected_functions(target_tree, func_names, func_wrapped="main",
                                                  loc_to_inject=loc_to_inject)
            else:
                if loc_to_inject == "main":
                    append_injected_functions_before_main(target_tree, func_names)
                elif loc_to_inject == "end":
                    append_injected_functions_after_main(target_tree, func_names)

        # Convert the modified AST back to Python code
        modified_code = astor.to_source(target_tree)

        # Determine the output file name
        if new_name == "":
            # Generate a default modified file name
            base, ext = os.path.splitext(src_code_filename)
            modified_name = f"{base}_modified{ext}"
        else:
            if not new_name.endswith(".py"):
                modified_name = new_name.strip() + ".py"
            else:
                modified_name = new_name.strip()

        # Ensure the output directory exists
        output_dir = os.path.dirname(modified_name)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the modified code back to the target script
        with open(modified_name, 'w') as src_code:
            src_code.write(modified_code)

        print(f"Code has been injected into the target script. Saved as: {modified_name}")
        return 0

    except Exception as e:
        print(f"An error occurred, please debug this: {e}.")
        return 1
