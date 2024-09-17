import ast
import astor


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


def import_exists(imports, target_tree):
    """
    Function to check if the import already exists in the target script
    :param imports:
    :param target_tree:
    :return:
    """
    existing_imports = [node for node in target_tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]

    for new_import in imports:
        for existing_import in existing_imports:
            if ast.dump(existing_import) == ast.dump(new_import):
                return True
    return False


def wrap_main_with_injected_function(tree, func_name, func_wrapped="main"):
    """
        This function wraps the injected call as a condition before letting main be called
        Modify the __main__ block to wrap main() inside injected_function()
        :param tree:
        :param injected_call:
        :return 0:
        """
    # Construct the call to `injected_function()`
    injected_call = ast.Call(func=ast.Name(id=func_name, ctx=ast.Load()), args=[], keywords=[])

    # Construct the new if block
    new_if_stmt = ast.If(
        test=ast.Compare(
            left=injected_call,
            ops=[ast.Eq()],
            comparators=[ast.Constant(value=1)]
        ),
        body=[ast.Expr(value=ast.Call(func=ast.Name(id=func_wrapped, ctx=ast.Load()), args=[], keywords=[]))],
        orelse=[]
    )

    # Find the `if __name__ == '__main__':` block
    for node in tree.body:
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare):
                # Modify the __main__ block to wrap the main() call with injected_function()
                node.body = [new_if_stmt]
    return 0


def append_injected_function_bfr_main(tree, injected_call):
    """
    This function appends the injected call to right before ethe main() function is called
    :param tree:
    :param injected_call:
    :return 0:
    """
    # Find the 'if __name__ == "__main__"' block and inject the function call there
    for node in tree.body:
        if isinstance(node, ast.If):
            # Look for the "__main__" condition
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                    # Inject the function call at the start of the "if __name__ == '__main__':" block
                    node.body.insert(0, injected_call)
    return 0


def embed_code(embed_code_filename="mal_code.py", src_code_filename='target_script.py', loc_to_inject="main",
               func_name="injected_function",
               wrap=True, new_name=""):
    """
    Function will take in code to embed along with the source file and perform transformation on it depending on the
    customization done to it. It can wrap the main function with the injected code or append the injected code
    embed_code_filename     (Filename of code to embed)
    imports                 (imports of the code content)
    src_code_filename       (Filename that you want to embed code into)
    loc_to_inject           (main/end the loc of code where you want to put the injected function)
    func_name               (Name of the injected function)
    wrap                    (True/False Whether you want to wrap as an if else condition pre-running main() func)
    new_name                (The new name for the modified code)
    :param new_name:
    :param embed_code_filename:
    :param src_code_filename:
    :param loc_to_inject:
    :param func_name:
    :param wrap:
    :return:
    """
    try:
        # Define the Python code to embed
        # code_to_embed = """def injected_function():
        #     print("This function was injected into the script.")"""

        # Parse the code to embed into an AST node
        # node_to_inject = ast.parse(code_to_embed)
        # extract imports and functions from

        # Extract the imports and functions of injectable code
        imports, functions = extract_functions_and_imports(embed_code_filename)

        # Load and parse the target Python script
        with open(src_code_filename, 'r') as src_file:
            target_code = src_file.read()

        # Parse the target code into an AST
        target_tree = ast.parse(target_code)

        # Inject imports if they don't already exist in the target script
        if not import_exists(imports, target_tree):
            target_tree.body = imports + target_tree.body

        # The function call to be inserted into code
        injected_call = ast.Expr(
            value=ast.Call(func=ast.Name(id=func_name, ctx=ast.Load()), args=[], keywords=[]))

        # If set to wrap main in if else condition else will just append at the top before main()
        if wrap:
            wrap_main_with_injected_function(target_tree, func_name, loc_to_inject)
        else:
            append_injected_function_bfr_main(target_tree, injected_call)

        # Inject the code into the script
        if loc_to_inject == "main":
            # Inject the function definition at the start of the file (right after imports)
            injection_point = 1  # Assuming imports are at the start, inject after them
            # target_tree.body[injection_point:injection_point] = node_to_inject.body
            target_tree.body[injection_point:injection_point] = functions

        elif loc_to_inject == "end":
            # Inject the code at the end of the target script
            # target_tree.body.extend(node_to_inject.body)
            target_tree.body.extend(functions)

        # Convert the modified AST back to Python code
        modified_code = astor.to_source(target_tree)

        if new_name == "":
            # Get the front of the file and add modified to the back of it.
            modified_name = src_code_filename.split(".py")[0] + '_modified.py'
        else:
            if ".py" in new_name:
                modified_name = new_name
            else:
                modified_name = new_name.strip() + ".py"

        # Write the modified code back to the target script
        with open(modified_name, 'w') as src_file:
            src_file.write(modified_code)

        print("Code has been injected into the target script.")
        return 0
    except:
        print("An error occurred, please debug this.")
        return 1


if __name__ == '__main__':
    # Define my file names
    inj_file = "mal_code.py"
    new_name = "Result/mal_2.py"
    src_file = "testcode.py"

    # normal wrapped main test
    embed_status = embed_code(embed_code_filename=inj_file, src_code_filename=src_file, new_name=new_name)

    new_name = "Result/mal_3.py"
    # append test
    embed_status = embed_code(embed_code_filename=inj_file, src_code_filename=src_file, new_name=new_name, wrap=False)
