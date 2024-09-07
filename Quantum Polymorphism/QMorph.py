import zlib
import random
import string
from binascii import hexlify


class Obfuscator:
    def __init__(self, content: str, clean=True, obfuscate_vars=True, obfuscate_strings=True, rename_imports=True,
                 randomize_lines=True, add_noise=True):
        self.content = content
        self.cleaned_content = None
        self.variables = {}
        self.renamed_imports = {}
        self.fake_code_lines = []
        self.obfuscated_strings = {}

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

        self.compressed_content = self.compress_script()

    def clean_code(self):
        """Remove comments and extra whitespace"""
        lines = self.content.splitlines()
        self.cleaned_content = "\n".join(line for line in lines if line.strip() and not line.strip().startswith("#"))

    def rename_variables(self):
        """Rename variables to random names"""
        tokens = self.content.splitlines()
        new_tokens = []
        for token in tokens:
            if token.isidentifier() and not token.startswith('__'):
                if token not in self.variables:
                    self.variables[token] = self._generate_random_string()
                new_tokens.append(self.variables[token])
            else:
                new_tokens.append(token)
        self.cleaned_content = "\n".join(new_tokens)

    def obfuscate_strings(self):
        """Obfuscate string literals"""
        tokens = self.cleaned_content.splitlines()
        new_tokens = []
        for token in tokens:
            if token.startswith('\'') or token.startswith('"'):  # String literals
                encoded_string = self._encode_string(token)
                new_tokens.append(encoded_string)
            else:
                new_tokens.append(token)
        self.cleaned_content = "\n".join(new_tokens)

    def rename_imports(self):
        """Rename imported libraries"""
        lines = self.cleaned_content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("import") or line.startswith("from"):
                import_name = line.split(" ")[1]
                new_import_name = self._generate_random_string()
                self.renamed_imports[import_name] = new_import_name
                lines[i] = line.replace(import_name, new_import_name)
        self.cleaned_content = "\n".join(lines)

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
        """Compress the script with zlib and hexlify"""
        print("Obfuscated content before compression:")
        print(self.cleaned_content)  # Print the obfuscated script before compressing
        compressed_content = zlib.compress(self.cleaned_content.encode('utf-8'))
        return hexlify(compressed_content).decode('utf-8')

    def _encode_string(self, string_literal):
        """Obfuscate a string by converting it into a hex-encoded string"""
        return "''.join([chr(int(c, 16)) for c in '{}'.split()])".format(
            ' '.join([hex(ord(c))[2:] for c in string_literal]))

    def _generate_random_string(self, length=10):
        """Generate random alphanumeric strings for renaming purposes"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def create_obfuscated_script(self, output_filepath):
        """Create the final script that combines the obfuscated payload with a front code"""
        front_script = """
# Harmless-looking front script
def dummy_front():
    print("This is just a simple front-end script.")
    return 42

if __name__ == "__main__":
    dummy_front()

# Obfuscated Payload (compressed and hidden)
import zlib
exec(zlib.decompress(bytes.fromhex('{compressed_payload}')))
""".format(compressed_payload=self.compressed_content)

        with open(output_filepath, "w") as f:
            f.write(front_script)


# Usage Example:
def main():
    # Step 1: Read the input script
    with open('test.py', 'r') as f:
        script_content = f.read()

    # Step 2: Obfuscate the script
    obfuscator = Obfuscator(content=script_content, clean=True, obfuscate_vars=True, obfuscate_strings=True,
                            rename_imports=True, randomize_lines=True, add_noise=True)

    # Step 3: Create the final script with obfuscated content embedded
    output_file = 'final_obfuscated_script.py'
    obfuscator.create_obfuscated_script(output_file)

    print(f"Obfuscated script saved as: {output_file}")


if __name__ == "__main__":
    main()
