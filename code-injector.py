import os
import sys
import subprocess
import tempfile

def print_usage():
    """Display usage information for the script."""
    print("""
Usage: python3 code_injector.py [-h | --help]

This script injects Python code into a target Python file or .deb package.
If no arguments are provided, it will prompt for:
  - Path to the target Python file or .deb package
  - Path to the file containing the code to inject
  - Injection mode (append or replace)
For .deb files, it will also prompt for the internal file path to modify.

Options:
  -h, --help    Show this help message and exit

Example:
  python3 code_injector.py
    (Follow the interactive prompts to specify files and mode)

Notes:
- For .deb files, requires `dpkg-deb` command available (Debian/Ubuntu).
- Back up files/packages before injection.
""")

def inject_code(target_file, code_to_inject, mode='append'):
    """
    Inject Python code into a target Python file.
    
    Args:
        target_file (str): Path to the target Python file
        code_to_inject (str): Python code to inject
        mode (str): 'append' to add code at the end, 'replace' to overwrite the file
    """
    try:
        # Check if target file exists
        if not os.path.isfile(target_file):
            print(f"Error: Target file {target_file} does not exist.")
            return False

        # Read original content if appending
        original_content = ''
        if mode == 'append':
            with open(target_file, 'r') as file:
                original_content = file.read()

        # Prepare new content
        new_content = code_to_inject if mode == 'replace' else original_content + '\n\n' + code_to_inject

        # Write the new content to the file
        with open(target_file, 'w') as file:
            file.write(new_content)
        
        print(f"Code successfully injected into {target_file} in {mode} mode.")
        return True

    except PermissionError:
        print(f"Error: Permission denied while accessing {target_file}.")
        return False
    except Exception as e:
        print(f"Error injecting code: {str(e)}")
        return False

def inject_into_deb(deb_file, internal_path, code_to_inject, mode='append', output_deb=None):
    """
    Inject Python code into a file inside a .deb package.
    
    Args:
        deb_file (str): Path to the .deb file
        internal_path (str): Relative path inside the package to the target file
        code_to_inject (str): Python code to inject
        mode (str): 'append' or 'replace'
        output_deb (str): Path for the output .deb (defaults to overwriting input)
    """
    if output_deb is None:
        output_deb = deb_file

    try:
        # Check if deb file exists
        if not os.path.isfile(deb_file):
            print(f"Error: .deb file {deb_file} does not exist.")
            return False

        with tempfile.TemporaryDirectory() as temp_dir:
            # Unpack the .deb
            subprocess.run(['dpkg-deb', '-x', deb_file, temp_dir], check=True, capture_output=True)
            
            # Full path to internal file
            internal_full = os.path.join(temp_dir, internal_path)
            if not os.path.isfile(internal_full):
                print(f"Error: Internal file '{internal_path}' not found in the .deb package.")
                # Optionally list files for debugging
                print("Available files in package:")
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), temp_dir)
                        print(f"  {rel_path}")
                return False
            
            # Inject code into the internal file
            if not inject_code(internal_full, code_to_inject, mode):
                return False
            
            # Repack the .deb
            subprocess.run(['dpkg-deb', '-b', temp_dir, output_deb], check=True, capture_output=True)
        
        print(f"Code successfully injected into '{internal_path}' and repacked to {output_deb}.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error with dpkg-deb: {e}")
        return False
    except Exception as e:
        print(f"Error injecting into .deb: {str(e)}")
        return False

def main():
    # Check for help flag
    if len(sys.argv) > 1 and (sys.argv[1] in ['-h', '--help']):
        print_usage()
        sys.exit(0)

    # Prompt for target file
    target_file = input("Enter the path to the target Python file or .deb package: ").strip()
    
    # Validate target file exists
    if not os.path.isfile(target_file):
        print(f"Error: {target_file} does not exist or is not a file.")
        return

    # Prompt for code file
    code_file = input("Enter the path to the file containing the code to inject: ").strip()
    
    # Validate code file
    if not os.path.isfile(code_file):
        print(f"Error: {code_file} does not exist or is not a file.")
        return

    # Read code to inject
    try:
        with open(code_file, 'r') as file:
            code_to_inject = file.read()
    except Exception as e:
        print(f"Error reading code file: {str(e)}")
        return

    # Prompt for injection mode
    mode = input("Enter injection mode (append/replace): ").strip().lower()
    if mode not in ['append', 'replace']:
        print("Error: Mode must be 'append' or 'replace'.")
        return

    # Handle .deb or regular file
    if target_file.endswith('.deb'):
        internal_path = input("Enter the relative path inside the .deb to inject into (e.g., usr/bin/app.py): ").strip()
        if not internal_path:
            print("Error: Internal path is required for .deb files.")
            return
        
        output_deb = input(f"Enter the output .deb file path (press Enter to overwrite '{target_file}'): ").strip()
        if not output_deb:
            output_deb = target_file
            print(f"Warning: Overwriting original .deb file '{target_file}'. Back it up first!")
        
        inject_into_deb(target_file, internal_path, code_to_inject, mode, output_deb)
    else:
        # Assume it's a Python file
        inject_code(target_file, code_to_inject, mode)

if __name__ == "__main__":
    main()
