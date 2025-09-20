import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
def parse_nl(text):
    """
    Parse natural language `text` into a list of shell commands
    using Google Gemini API. Returns list of command strings.
    """
    # Naive fallback patterns
    low = text.lower().strip()
    if low.startswith('make new folder called ') or low.startswith('create new folder called '):
        name = text[len('make new folder called '):].strip() if 'make' in low else text[len('create new folder called '):].strip()
        return [f'mkdir {name}']
    elif 'create a new folder' in low and 'called' in low:
        # Extract folder name after "called"
        parts = text.split('called')
        if len(parts) > 1:
            name = parts[1].strip().split()[0]  # Get first word after "called"
            return [f'mkdir {name}']
    elif 'clear' in low and ('terminal' in low or 'screen' in low):
        return ['clear']
    elif low.strip() in ['clear', 'cls']:
        return ['clear']
    elif 'create a file' in low and 'write' in low:
        # Handle: "create a file named hello.py and write code print("hello world") in it"
        words = text.lower().split()
        try:
            # Find filename
            if 'named' in words:
                named_idx = words.index('named')
                filename = text.split()[named_idx + 1]
            elif 'called' in words:
                called_idx = words.index('called')
                filename = text.split()[called_idx + 1]
            else:
                filename = 'newfile.txt'
            
            # Extract content after "write" or "code"
            if 'write code' in text.lower():
                content_start = text.lower().find('write code') + len('write code')
                content = text[content_start:].strip()
                if content.endswith(' in it'):
                    content = content[:-6].strip()
            elif 'write' in text.lower():
                content_start = text.lower().find('write') + len('write')
                content = text[content_start:].strip()
                if content.endswith(' in it'):
                    content = content[:-6].strip()
            else:
                content = ""
            
            if content:
                return [f'write {filename} "{content}"']
            else:
                return [f'touch {filename}']
        except:
            pass
    elif 'execute' in low or 'run' in low:
        # Handle: "execute hello.py" or "run hello.py"
        words = text.split()
        try:
            if 'execute' in words:
                exec_idx = words.index('execute')
                if exec_idx + 1 < len(words):
                    filename = words[exec_idx + 1]
                    return [f'python {filename}']
            elif 'run' in words:
                run_idx = words.index('run')
                if run_idx + 1 < len(words):
                    filename = words[run_idx + 1]
                    return [f'python {filename}']
        except:
            pass
        # Simple pattern: "move file1.txt into test"
        words = text.split()
        try:
            move_idx = [i for i, w in enumerate(words) if w.lower() == 'move'][0]
            into_idx = [i for i, w in enumerate(words) if w.lower() == 'into'][0]
            if move_idx < into_idx:
                source = words[move_idx + 1]
                dest = words[into_idx + 1]
                return [f'mv {source} {dest}/']
        except:
            pass
    # Load API key from .env
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return []
    # Configure Google Gemini API
    genai.configure(api_key=api_key)
    prompt = (
        "Convert this user instruction into simple shell commands. "
        "IMPORTANT: Use only these exact commands and syntax:\n"
        "- ls, ls -l (list files)\n"
        "- pwd (current directory)\n"
        "- cd dirname (change directory)\n"
        "- mkdir dirname (create directory)\n"
        "- rm filename, rm -rf dirname (remove files/dirs)\n"
        "- cat filename (read file)\n"
        "- touch filename (create empty file)\n"
        "- mv source dest (move/rename)\n"
        "- write filename \"content\" (create file with content)\n"
        "- echo \"text\" > filename (write text to file)\n"
        "- python filename.py (execute Python file)\n"
        "- run filename.py (execute Python file)\n"
        "- cpu, mem, ps (system info)\n\n"
        "For creating files with content, use: write filename \"content\"\n"
        "Do NOT use complex shell syntax like <<EOF, pipes, or advanced redirections.\n"
        f"User instruction: {text}\n"
        "Commands:"
    )
    try:
        # Use GenerativeModel for Gemini with timeout and safety settings
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Add generation config for better control
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 100,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            stream=False
        )
        
        if not response or not response.text:
            return []
            
        content = response.text.strip()
        commands = [line.strip() for line in content.splitlines() if line.strip()]
        
        # Filter out any non-command text and explanations
        valid_commands = []
        for cmd in commands:
            cmd_clean = cmd.strip()
            # Skip lines that look like explanations
            if cmd_clean.startswith('#') or cmd_clean.startswith('//') or ':' in cmd_clean[:10]:
                continue
            # Only accept lines that start with known commands
            if any(cmd_clean.startswith(c + ' ') or cmd_clean == c for c in ['ls', 'pwd', 'cd', 'mkdir', 'rm', 'cat', 'touch', 'mv', 'cpu', 'mem', 'ps', 'echo', 'write', 'python', 'run', 'execute']):
                valid_commands.append(cmd_clean)
        
        return valid_commands[:3]  # Limit to max 3 commands to prevent issues
        
    except Exception as e:
        print(f"AI parsing error: {e}")
        return []
