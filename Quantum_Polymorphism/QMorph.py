import zlib
import random
import string
import builtins
from binascii import hexlify
import ast
import textwrap
import os  # Added for directory and file handling
from qiskit import QuantumCircuit
from qiskit.execute_function import execute
from qiskit_aer import AerSimulator


class Obfuscator:
    def __init__(self, content: str, clean=True, obfuscate_vars=True, obfuscate_strings=True,
                 rename_imports=True, randomize_lines=True, add_noise=True, use_qrng=False):
        self.content = content
        self.cleaned_content = None
        self.variables = {}
        self.renamed_imports = {}
        self.fake_code_lines = []
        self.obfuscated_strings = {}
        self.imported_modules = set()
        self.use_qrng = use_qrng
        self.renamed_vars = {}  # Initialize renamed_vars

        if clean:
            self.clean_code()

        if rename_imports:
            self.rename_imports()

        if obfuscate_vars:
            self.rename_variables()

        if obfuscate_strings:
            self.obfuscate_strings()

        if randomize_lines:
            self.randomize_code_safely()

        if add_noise:
            self.add_noise_to_code()

        # Compress the cleaned and obfuscated content
        self.compressed_content = self.compress_script()

    def clean_code(self):
        """Remove comments and extra whitespace"""
        lines = self.content.splitlines()
        self.cleaned_content = "\n".join(
            line for line in lines if line.strip() and not line.strip().startswith("#")
        )

    def rename_imports(self):
        """Collect imported modules using AST without renaming them"""

        class ImportRenamer(ast.NodeVisitor):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator

            def visit_Import(self, node):
                for alias in node.names:
                    asname = alias.asname if alias.asname else alias.name
                    self.obfuscator.imported_modules.add(asname)
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                if node.module:
                    self.obfuscator.imported_modules.add(node.module)
                for alias in node.names:
                    asname = alias.asname if alias.asname else alias.name
                    self.obfuscator.imported_modules.add(asname)
                self.generic_visit(node)

        tree = ast.parse(self.cleaned_content)
        renamer = ImportRenamer(self)
        renamer.visit(tree)
        self.cleaned_content = ast.unparse(tree)

    def rename_variables(self):
        """Rename variables, functions, and classes to random names using AST."""

        class VariableRenamer(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator
                self.renamed_vars = {}
                self.builtin_names = set(dir(builtins))
                # Include imported module names in essential names to avoid renaming them
                self.essential_names = (
                        set(obfuscator.renamed_imports.values())
                        | obfuscator.imported_modules
                )

            def visit_FunctionDef(self, node):
                # Rename the function name
                if node.name not in self.essential_names and not node.name.startswith(
                        '__') and node.name not in self.builtin_names:
                    new_name = self.obfuscator._generate_unique_random_string('method')
                    self.renamed_vars[node.name] = new_name
                    node.name = new_name

                # Rename arguments
                if node.args:
                    for arg in node.args.args:
                        if arg.arg not in self.renamed_vars and arg.arg not in self.essential_names:
                            new_name = self.obfuscator._generate_unique_random_string('variable')
                            self.renamed_vars[arg.arg] = new_name
                        if arg.arg in self.renamed_vars:
                            arg.arg = self.renamed_vars[arg.arg]
                self.generic_visit(node)
                return node

            def visit_ClassDef(self, node):
                # Rename the class name
                if node.name not in self.essential_names and not node.name.startswith('__'):
                    new_name = self.obfuscator._generate_unique_random_string('class')
                    self.renamed_vars[node.name] = new_name
                    node.name = new_name
                self.generic_visit(node)
                return node

            def visit_Name(self, node):
                if node.id in self.renamed_vars:
                    node.id = self.renamed_vars[node.id]
                elif (node.id not in self.essential_names
                      and not node.id.startswith('__')
                      and node.id not in self.builtin_names):
                    new_name = self.obfuscator._generate_unique_random_string('variable')
                    self.renamed_vars[node.id] = new_name
                    node.id = new_name
                return node

            def visit_Attribute(self, node):
                self.generic_visit(node)
                return node  # Do not rename attributes to avoid breaking code

            def visit_Global(self, node):
                # Rename global variable names
                for i, name in enumerate(node.names):
                    if name in self.renamed_vars:
                        node.names[i] = self.renamed_vars[name]
                    else:
                        if name not in self.essential_names:
                            new_name = self.obfuscator._generate_unique_random_string('variable')
                            self.renamed_vars[name] = new_name
                            node.names[i] = new_name
                return node

            def visit_Nonlocal(self, node):
                # Rename nonlocal variable names
                for i, name in enumerate(node.names):
                    if name in self.renamed_vars:
                        node.names[i] = self.renamed_vars[name]
                    else:
                        if name not in self.essential_names:
                            new_name = self.obfuscator._generate_unique_random_string('variable')
                            self.renamed_vars[name] = new_name
                            node.names[i] = new_name
                return node

        tree = ast.parse(self.cleaned_content)
        renamer = VariableRenamer(self)
        tree = renamer.visit(tree)
        self.cleaned_content = ast.unparse(tree)
        self.renamed_vars = renamer.renamed_vars  # Assign renamed_vars to Obfuscator

    def obfuscate_strings(self):
        """Obfuscate string literals using AST."""

        class StringObfuscator(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator

            def visit_Constant(self, node):
                if isinstance(node.value, str):
                    # Skip obfuscating code strings
                    if self.is_code_string(node.value):
                        return node
                    new_value = self.obfuscator._encode_string(node.value)
                    return ast.parse(new_value).body[0].value
                return node

            def visit_JoinedStr(self, node):
                # Recursively visit each value in the JoinedStr
                for idx, value in enumerate(node.values):
                    if isinstance(value, ast.Str):
                        new_value = self.obfuscator._encode_string(value.s)
                        node.values[idx] = ast.Constant(value=new_value)
                    else:
                        self.visit(value)  # Recursively handle other types
                return node

            def is_code_string(self, value):
                # Simple heuristic to detect code strings
                keywords = ['def', 'class', 'import', 'exec', 'eval']
                return any(kw in value for kw in keywords)

        tree = ast.parse(self.cleaned_content)
        obfuscator = StringObfuscator(self)
        tree = obfuscator.visit(tree)
        self.cleaned_content = ast.unparse(tree)

    def randomize_code_safely(self):
        """Shuffle independent, non-control structure code lines within functions."""

        class CodeRandomizer(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator

            def visit_FunctionDef(self, node):
                # Separate shufflable and non-shufflable statements
                shufflable = []
                non_shufflable = []
                for stmt in node.body:
                    if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.Expr, ast.Pass)):
                        shufflable.append(stmt)
                    else:
                        non_shufflable.append(stmt)

                # Shuffle the shufflable statements
                random.shuffle(shufflable)

                # Reconstruct the function body, preserving the order of non-shufflable statements
                node.body = shufflable + non_shufflable

                # Continue traversing
                self.generic_visit(node)
                return node

            def visit_ClassDef(self, node):
                # Process methods inside the class
                for idx, item in enumerate(node.body):
                    if isinstance(item, ast.FunctionDef):
                        node.body[idx] = self.visit_FunctionDef(item)
                return node

        tree = ast.parse(self.cleaned_content)
        randomizer = CodeRandomizer(self)
        tree = randomizer.visit(tree)
        self.cleaned_content = ast.unparse(tree)

    def add_noise_to_code(self):
        """Maintain the structure of the code without inserting fake lines of code."""
        lines = self.cleaned_content.splitlines()
        final_lines = []
        current_indent = 0
        inside_block = False  # Track if we're inside a block of code

        for line in lines:
            stripped_line = line.strip()

            # Handle top-level lines (imports, main block)
            if stripped_line.startswith("import") or stripped_line.startswith("def") or stripped_line.startswith(
                    "if __name__"):
                final_lines.append(line)
                current_indent = 0  # Reset indentation for top-level code
                inside_block = False  # Exit any blocks
                continue

            # Skip empty lines or preserve them
            if not stripped_line:
                final_lines.append(line)
                continue

            # Handle control structures or function definitions
            if stripped_line.endswith(":"):
                final_lines.append(line)
                current_indent = len(line) - len(line.lstrip())  # Track the current indentation level
                inside_block = True  # We're inside a block after control structure

            elif inside_block:
                # Inside a block, just maintain the correct indentation for block contents
                indent_level = current_indent + 4  # Standard indentation level after control structure
                final_lines.append(" " * indent_level + stripped_line)
                inside_block = False  # Exit block after processing the content

            else:
                # Regular lines, maintain indentation level
                indent_level = len(line) - len(line.lstrip())
                final_lines.append(" " * indent_level + stripped_line)

        # Combine the final lines into the final cleaned content
        self.cleaned_content = "\n".join(final_lines)

    def compress_script(self):
        """Compress the obfuscated input script with zlib and hexlify"""
        # Uncomment the next line to see the obfuscated script before compression
        # print(self.cleaned_content)
        compressed_content = zlib.compress(self.cleaned_content.encode('utf-8'))
        return hexlify(compressed_content).decode('utf-8')

    def _encode_string(self, string_literal):
        """Obfuscate a string by converting it into a list of character codes."""
        encoded_chars = ','.join(str(ord(c)) for c in string_literal)
        return f"''.join([chr(n) for n in [{encoded_chars}]])"

    def _generate_random_string_from_list(self, category):
        """Generate a random string from predefined lists based on category."""
        if category == 'class':
            return self._generate_random_string_from_qrng_list(self.COMMON_CLASS_NAMES)
        elif category == 'method':
            return self._generate_random_string_from_qrng_list(self.COMMON_METHOD_NAMES)
        elif category == 'variable':
            return self._generate_random_string_from_qrng_list(self.COMMON_VARIABLE_NAMES)
        else:
            return self._generate_random_string()

    def _generate_unique_random_string(self, category, max_attempts=1000):
        """Generate a unique random string from predefined lists based on category."""
        for _ in range(max_attempts):
            name = self._generate_random_string_from_list(category)
            if name not in self.renamed_imports.values() and name not in self.renamed_vars.values():
                return name
        raise ValueError(f"Failed to generate a unique name for category '{category}' after {max_attempts} attempts.")

    def _generate_random_string_from_qrng_list(self, name_list):
        """Generate a random string from a provided list using QRNG or classical RNG."""
        try:
            if self.use_qrng:
                # Determine the number of bits needed for indexing
                bits_needed = len(name_list).bit_length()
                random_bits = self.generate_qrng_bits(bits_needed)
                if not random_bits:
                    raise ValueError("No random bits generated by QRNG.")
                random_index = int(random_bits, 2) % len(name_list)
                return name_list[random_index]
            else:
                # Use classical RNG
                return random.choice(name_list)
        except Exception as e:
            print(f"QRNG failed: {e}. Falling back to classical RNG.")
            return random.choice(name_list)

    def generate_qrng_bits(self, num_bits=16):
        """Generate quantum random bits using Qiskit."""
        simulator = AerSimulator()
        random_bits = ""

        try:
            batches = num_bits // 16
            remaining_bits = num_bits % 16

            for batch_num in range(batches):
                print(f"Executing batch {batch_num + 1}/{batches}")
                qc = QuantumCircuit(16, 16)
                qc.h(range(16))  # Apply Hadamard gate to each qubit
                qc.measure(range(16), range(16))

                # Execute the circuit
                job = execute(qc, simulator, shots=1)
                result = job.result()

                # Get counts
                counts = result.get_counts(qc)
                print(f"Counts for batch {batch_num + 1}: {counts}")

                if not counts:
                    raise ValueError("No counts returned from QRNG.")

                # Extract measured bits
                measured_bits = list(counts.keys())[0]
                print(f"Measured bits for batch {batch_num + 1}: {measured_bits}")
                random_bits += measured_bits

            # Handle remaining bits if num_bits is not a multiple of 16
            if remaining_bits > 0:
                qc = QuantumCircuit(remaining_bits, remaining_bits)
                qc.h(range(remaining_bits))
                qc.measure(range(remaining_bits), range(remaining_bits))

                job = execute(qc, simulator, shots=1)
                result = job.result()
                counts = result.get_counts(qc)

                if not counts:
                    raise ValueError("No counts returned from QRNG for remaining bits.")

                measured_bits = list(counts.keys())[0]
                random_bits += measured_bits

            return random_bits[:num_bits]

        except Exception as e:
            print(f"Error generating QRNG bits: {e}")
            raise e  # Propagate exception to fallback mechanism

    def _generate_random_string(self, length=5):
        """Generate random alphanumeric strings for renaming purposes using QRNG or classical RNG."""
        try:
            if self.use_qrng:
                # Generate sufficient bits to cover the character space
                bits_needed = length * 6  # Approximate bits needed (since 2^6 = 64 > 62 possible characters)
                random_bits = self.generate_qrng_bits(bits_needed)
                if not random_bits:
                    raise ValueError("No random bits generated by QRNG.")
                chars = []
                for i in range(0, len(random_bits), 6):
                    chunk = random_bits[i:i + 6]
                    if len(chunk) < 6:
                        chunk = chunk.ljust(6, '0')  # Pad the last chunk if necessary
                    index = int(chunk, 2) % len(string.ascii_letters + string.digits + '_')
                    chars.append((string.ascii_letters + string.digits + '_')[index])
                return ''.join(chars)
            else:
                # Use classical RNG
                first_char = random.choice(string.ascii_letters + '_')
                other_chars = ''.join(random.choices(string.ascii_letters + string.digits + '_', k=length - 1))
                return first_char + other_chars
        except Exception as e:
            print(f"QRNG failed: {e}. Falling back to classical RNG.")
            # Fallback to classical RNG
            first_char = random.choice(string.ascii_letters + '_')
            other_chars = ''.join(random.choices(string.ascii_letters + string.digits + '_', k=length - 1))
            return first_char + other_chars

    # Predefined lists of common, meaningful names
    COMMON_CLASS_NAMES = [
        "DataManager", "Processor", "Handler", "Controller", "Manager",
        "Service", "Utility", "Calculator", "Generator", "Parser",
        "Executor", "Coordinator", "Director", "Supervisor", "Navigator",
        "Assistant", "Optimizer", "Transformer", "Analyzer", "Mediator"
    ]

    COMMON_METHOD_NAMES = [
        "initialize", "process", "handle", "compute", "execute",
        "run", "start", "stop", "update", "delete", "create", "read",
        "write", "load", "save", "transform", "analyze", "optimize", "navigate", "coordinate"
    ]

    COMMON_VARIABLE_NAMES = [
        "data", "result", "input_data", "output_data", "config",
        "settings", "counter", "status", "value", "temp", "item",
        "index", "error", "message", "flag", "buffer", "object", "parameter", "context", "record"
    ]

    # Helper methods for random code generation
    def _rand_var_names(self, count):
        """Generate a list of random variable names from predefined lists."""
        var_names = []
        for _ in range(count):
            category = random.choice(['class', 'method', 'variable'])
            var_name = self._generate_unique_random_string(category)
            # Ensure uniqueness by appending a random number
            var_name += ''.join(random.choices(string.digits, k=2))
            var_names.append(var_name)
        return var_names

    def _rand_int(self):
        """Generate a random integer."""
        return random.randint(-100000, 100000)

    def _rand_op(self):
        """Choose a random operator."""
        return random.choice(['+', '-', '*', '/'])

    def _rand_type(self):
        """Choose a random type."""
        return random.choice(['int', 'str', 'list', 'dict', 'set', 'bool', 'float', 'complex'])

    def _rand_bool(self, less_than=True):
        """Generate a random boolean expression."""
        op = '<' if less_than else '>'
        return f"{random.randint(1, 1000)} {op} {random.randint(1001, 2000)}"

    def _rand_code_block(self):
        """Generate a random code block."""
        var_names = self._rand_var_names(3)
        code = f"{var_names[0]} = {self._rand_int()} {self._rand_op()} {self._rand_int()}\n"
        code += f"if {self._rand_bool()}:\n"
        code += f"    {var_names[1]} = {self._rand_type()}({var_names[0]})\n"
        code += f"else:\n"
        code += f"    {var_names[2]} = {self._rand_type()}()\n"
        return code

    def _rand_pass(self, line=True):
        """Generate a random pass statement or code block."""
        if line:
            return "pass"
        else:
            return self._rand_code_block()

    def _indent_code_block(self, code_block: str, indent_spaces: int):
        """Indent a code block by a specified number of spaces."""
        indentation = ' ' * indent_spaces
        indented_block = '\n'.join(indentation + line if line else line for line in code_block.splitlines())
        return indented_block

    def create_obfuscated_script(self, output_filepath):
        """Create the final script that combines the obfuscated payload with a dynamic front code."""
        # Generate random names for the placeholders from predefined lists
        class_name = self._generate_unique_random_string('class') + ''.join(random.choices(string.digits, k=2))
        method_name = self._generate_unique_random_string('method') + ''.join(random.choices(string.digits, k=2))
        another_method_name = self._generate_unique_random_string('method') + ''.join(
            random.choices(string.digits, k=2))
        execute_method_name = "execute"
        property_name = "_property"

        # Generate random code blocks
        creator = self._rand_code_block()
        rands = [self._rand_code_block() for _ in range(3)]
        vars_code = '\n'.join([f"{var} = {self._rand_int()}" for var in self._rand_var_names(5)])
        indented_vars_code = self._indent_code_block(vars_code, 8)  # Indent by 8 spaces for try block

        # Build the dynamic front script template similar to the user's previous format
        front_script_template = f"""
execute922, Handler059, data343, Calculator340, data406, Processor777, create101 = exec, str, tuple, map, ord, globals, type

class {class_name}:
    def __init__(self, Manager070):
        self.{method_name}(run753={self._rand_int()})

    def {method_name}(self, run753 = {self._rand_type()}):
{self._indent_code_block(creator, 8)}
        self.Service887 {self._rand_op()}= {self._rand_int()} {self._rand_op()} run753
{self._indent_code_block(rands[0], 8)}

    def {another_method_name}(self, Calculator874 = {self._rand_int()}):
{self._indent_code_block(creator, 8)}
        Calculator874 {self._rand_op()}= {self._rand_int()} {self._rand_op()} {self._rand_int()}
        self.temp980 != {self._rand_type()}
{self._indent_code_block(rands[1], 8)}

    def process763(self, item612 = {self._rand_type()}):
        return Processor777()[item612]

    def value263(self, Processor131 = {self._rand_int()} {self._rand_op()} {self._rand_int()}, create478 = {self._rand_type()}, Manager878 = Processor777):
{self._indent_code_block(creator, 8)}
        Manager878()[Processor131] = create478
        handle691 = {self._rand_int()} {self._rand_op()} {self._rand_int()}
        if {self._rand_bool()}:
{self._indent_code_block(rands[2], 12)}
        else:
            Manager924 = {self._rand_type()}()

    def {execute_method_name}(self, code = {self._rand_type()}):
        return execute922(Handler059(data343(Calculator340(data406, code))))

    @property
    def {property_name}(self):
        self.hjqTnRl8sl = '<__main__.Handler object at 0x000002598BE40120>'
        return (self.hjqTnRl8sl, {class_name}.{property_name})

if __name__ == '__main__':
    try:
        (lambda __, _e: _e(__('''{self.compressed_content}'''), globals()))(lambda x: __import__('zlib').decompress(bytes.fromhex(x)), exec)
        Handler883 = {class_name}(Manager070 = {self._rand_int()} {self._rand_op()} {self._rand_int()})

{indented_vars_code}

        pass
        pass

    except Exception as stop57:
        if {self._rand_bool(False)}:
            {class_name}.{execute_method_name}(code = Handler059(stop57))
        elif {self._rand_bool(False)}:
            {self._rand_pass()}
"""
        # Dedent the template to remove leading spaces
        front_script = textwrap.dedent(front_script_template)

        # Write the front script to the output file
        with open(output_filepath, "w") as f:
            f.write(front_script)

    # take out argparse, take out sys.exit, put return, boolean, outpufilename
def QMorph(input_file: str, output: str = None):
    """
    Obfuscate a Python script.

    Parameters:
        input_file (str): Path to the input Python script to be obfuscated.
        output (str, optional): Name for the output obfuscated script. If not provided,
                                a unique name will be generated in the Output directory.

    Returns:
        tuple: (True, output_file) if successful, (False, error_message) otherwise.
    """
    try:
        # Get the current directory where the script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Move one level up to the parent directory (ICT3215-Digital-Forensics)
        parent_dir = os.path.dirname(current_dir)

        # Define the output directory in the parent directory
        output_dir = os.path.join(parent_dir, "Output")

        # Create the directory if it doesn't already exist
        os.makedirs(output_dir, exist_ok=True)

        # Step 3: Determine the output filename
        if output:
            # If user provides an output filename, use it within the Output directory
            output_file = os.path.join(output_dir, output)
            # Ensure the file has a .py extension
            if not output_file.endswith('.py'):
                output_file += '.py'
        else:
            # Generate a unique filename with a counter
            base_name = "QmorphObf"
            extension = ".py"
            counter = 1
            while True:
                output_file = os.path.join(output_dir, f"{base_name}{counter}{extension}")
                if not os.path.exists(output_file):
                    break
                counter += 1

        # Step 4: Read the input script
        try:
            with open(input_file, 'r') as f:
                script_content = f.read()
        except FileNotFoundError:
            return (False, f"Error: The file '{input_file}' does not exist.")
        except IOError as e:
            return (False, f"Error reading '{input_file}': {e}")

        # Step 5: Obfuscate the script with the updated Obfuscator
        try:
            obfuscator = Obfuscator(
                content=script_content,
                clean=True,
                obfuscate_vars=True,
                obfuscate_strings=True,
                rename_imports=True,
                randomize_lines=True,
                add_noise=True,
                use_qrng=True
            )
        except Exception as e:
            return (False, f"Error initializing Obfuscator: {e}")

        # Step 6: Create the final script with obfuscated content embedded
        try:
            obfuscator.create_obfuscated_script(output_file)
        except Exception as e:
            return (False, f"Error creating obfuscated script '{output_file}': {e}")

        return (True, output_file)

    except Exception as e:
        return (False, f"Unexpected error: {e}")


# success,msg = QMorph("../Sample_Malware/browse_annoying_site.py")
# print(msg)
