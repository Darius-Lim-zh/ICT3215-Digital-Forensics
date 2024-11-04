import ast
import astor

class CodeFragmenter(ast.NodeTransformer):
    def __init__(self):
        self.function_counter = 0
        self.replacements = []
        self.global_vars = set()

    def visit_If(self, node):
        # Identify if-blocks as logical units
        self.generic_visit(node)  # Continue visiting the rest of the tree
        return self.split_into_function(node)

    def visit_While(self, node):
        # Identify while-blocks as logical units
        self.generic_visit(node)
        return self.split_into_function(node)

    def visit_Expr(self, node):
        # Process statements or expressions outside control structures
        if isinstance(node.value, ast.Call):
            return self.split_into_function(node)
        return node

    def visit_Assign(self, node):
        """Collect global variables from assignments"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.global_vars.add(target.id)
        return node

    def split_into_function(self, node):
        """Extracts the node and creates a new function"""
        self.function_counter += 1
        func_name = f"fragmented_function_{self.function_counter}"

        # Create a global declaration for all tracked global variables
        global_declarations = [
            ast.Global(names=[var]) for var in self.global_vars
        ]

        # Create a function definition with the extracted block
        func_def = ast.FunctionDef(
            name=func_name,
            args=ast.arguments(
                args=[], vararg=None, kwarg=None, defaults=[], kw_defaults=[]
            ),
            body=global_declarations + [node],  # Add global vars at the top
            decorator_list=[]
        )

        # Replace the original node with a function call
        func_call = ast.Expr(value=ast.Call(func=ast.Name(id=func_name, ctx=ast.Load()), args=[], keywords=[]))
        self.replacements.append(func_def)

        return func_call

    def finalize(self, tree):
        """Add all function definitions at the top of the script"""
        for func_def in self.replacements:
            tree.body.insert(0, func_def)
        return tree