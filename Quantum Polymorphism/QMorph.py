import zlib
import random
import argparse
import sys
import string
import builtins
from binascii import hexlify
import ast
import textwrap
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
                    new_name = self.obfuscator._generate_random_string_from_list('method')
                    self.renamed_vars[node.name] = new_name
                    node.name = new_name

                # Rename arguments
                if node.args:
                    for arg in node.args.args:
                        if arg.arg not in self.renamed_vars and arg.arg not in self.essential_names:
                            new_name = self.obfuscator._generate_random_string_from_list('variable')
                            self.renamed_vars[arg.arg] = new_name
                        if arg.arg in self.renamed_vars:
                            arg.arg = self.renamed_vars[arg.arg]
                self.generic_visit(node)
                return node

            def visit_ClassDef(self, node):
                # Rename the class name
                if node.name not in self.essential_names and not node.name.startswith('__'):
                    new_name = self.obfuscator._generate_random_string_from_list('class')
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
                    new_name = self.obfuscator._generate_random_string_from_list('variable')
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
                            new_name = self.obfuscator._generate_random_string_from_list('variable')
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
                            new_name = self.obfuscator._generate_random_string_from_list('variable')
                            self.renamed_vars[name] = new_name
                            node.names[i] = new_name
                return node

        tree = ast.parse(self.cleaned_content)
        renamer = VariableRenamer(self)
        tree = renamer.visit(tree)
        self.cleaned_content = ast.unparse(tree)

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

            def is_code_string(self, value):
                # Simple heuristic to detect code strings
                keywords = ['def', 'class', 'import', 'exec', 'eval']
                return any(kw in value for kw in keywords)

        tree = ast.parse(self.cleaned_content)
        obfuscator = StringObfuscator(self)
        tree = obfuscator.visit(tree)
        self.cleaned_content = ast.unparse(tree)

    def randomize_code_safely(self):
        """Shuffle non-top-level code lines without breaking critical control structures"""
        lines = self.cleaned_content.splitlines()
        top_level_lines = []
        non_top_level_lines = []
        inside_function = False
        inside_while_loop = False  # Track when inside while True block

        for line in lines:
            stripped_line = line.strip()
            # Keep top-level constructs intact
            if stripped_line.startswith("import") or stripped_line.startswith("def") or stripped_line.startswith(
                    "if __name__"):
                top_level_lines.append(line)
                inside_function = stripped_line.startswith("def")
                inside_while_loop = False  # Reset while-loop tracking when new top-level line
            elif inside_function and stripped_line.startswith("while True:"):
                # Keep "while True:" intact and avoid shuffling its contents
                top_level_lines.append(line)
                inside_while_loop = True  # Track that we are inside a while loop
            elif inside_while_loop and not stripped_line.startswith("while"):
                # Ensure the content inside the while loop is preserved correctly with proper indentation
                top_level_lines.append(line)
            elif inside_function and stripped_line and not stripped_line.startswith("while"):
                # Randomize only non-control structure lines inside functions
                non_top_level_lines.append(line)
            else:
                top_level_lines.append(line)

        # Shuffle non-critical lines (those inside function but not control structures)
        random.shuffle(non_top_level_lines)
        self.cleaned_content = "\n".join(top_level_lines + non_top_level_lines)

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
        print("Obfuscated content before compression:")
        print(self.cleaned_content)  # Print the obfuscated script before compressing
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

            print(f"Generating QRNG bits: {num_bits} bits, {batches} full batches, {remaining_bits} remaining bits.")

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
                print(f"Executing remaining {remaining_bits} bits.")
                qc = QuantumCircuit(remaining_bits, remaining_bits)
                qc.h(range(remaining_bits))
                qc.measure(range(remaining_bits), range(remaining_bits))

                job = execute(qc, simulator, shots=1)
                result = job.result()
                counts = result.get_counts(qc)
                print(f"Counts for remaining bits: {counts}")

                if not counts:
                    raise ValueError("No counts returned from QRNG for remaining bits.")

                measured_bits = list(counts.keys())[0]
                print(f"Measured bits for remaining bits: {measured_bits}")
                random_bits += measured_bits

            print(f"Total QRNG bits generated: {random_bits[:num_bits]}")
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
            var_name = self._generate_random_string_from_list(category)
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
        class_name = self._generate_random_string_from_list('class') + ''.join(random.choices(string.digits, k=2))
        method_name = self._generate_random_string_from_list('method') + ''.join(random.choices(string.digits, k=2))
        another_method_name = self._generate_random_string_from_list('method') + ''.join(
            random.choices(string.digits, k=2))
        execute_method_name = "execute"  # Keep execute as a standard method name
        property_name = "_property"  # Keeping property name as a standard name

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
        (lambda __, _e: _e(__('''{self.compressed_content}'''), globals()))(lambda x: __import__('zlib').decompress(bytes.fromhex(x)),exec)
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

    # Usage Example:


def main():
    # Step 1: Parse command-line arguments
    parser = argparse.ArgumentParser(description="Obfuscate a Python script.")
    parser.add_argument(
        'input_script',
        type=str,
        help='Path to the input Python script to be obfuscated.'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='final_obfuscated_script.py',
        help='Path for the output obfuscated script (default: final_obfuscated_script.py).'
    )

    args = parser.parse_args()

    input_file = args.input_script
    output_file = args.output

    # Step 2: Read the input script
    try:
        with open(input_file, 'r') as f:
            script_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading '{input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Obfuscate the script with the updated Obfuscator
    try:
        obfuscator = Obfuscator(
            content=script_content,
            clean=True,
            obfuscate_vars=True,
            obfuscate_strings=True,
            rename_imports=True,
            randomize_lines=True,
            add_noise=True,
            use_qrng=True  # Enable QRNG
        )
    except Exception as e:
        print(f"Error initializing Obfuscator: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 4: Create the final script with obfuscated content embedded
    try:
        obfuscator.create_obfuscated_script(output_file)
    except Exception as e:
        print(f"Error creating obfuscated script '{output_file}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Obfuscated script saved as: {output_file}")


if __name__ == "__main__":
    main()
