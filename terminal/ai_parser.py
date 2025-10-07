import os
import time
from collections import deque
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Rate limiting for Gemini API (12 requests per minute)
class APIRateLimiter:
    def __init__(self, max_requests=12, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times = deque()
    
    def can_make_request(self):
        """Check if we can make a request without exceeding rate limit"""
        current_time = time.time()
        
        # Remove requests older than the time window
        while self.request_times and current_time - self.request_times[0] > self.time_window:
            self.request_times.popleft()
        
        # Check if we're under the limit
        return len(self.request_times) < self.max_requests
    
    def record_request(self):
        """Record that we made a request"""
        self.request_times.append(time.time())
    
    def get_status(self):
        """Get current rate limit status"""
        current_time = time.time()
        
        # Clean old requests
        while self.request_times and current_time - self.request_times[0] > self.time_window:
            self.request_times.popleft()
        
        requests_made = len(self.request_times)
        requests_remaining = self.max_requests - requests_made
        
        # Calculate time until next request if at limit
        time_until_reset = 0
        if requests_made >= self.max_requests and self.request_times:
            oldest_request = self.request_times[0]
            time_until_reset = max(0, self.time_window - (current_time - oldest_request))
        
        return {
            'requests_made': requests_made,
            'requests_remaining': requests_remaining,
            'max_requests': self.max_requests,
            'time_window': self.time_window,
            'can_make_request': self.can_make_request(),
            'time_until_reset': time_until_reset
        }

# Global rate limiter instance
rate_limiter = APIRateLimiter()

def get_rate_limit_status():
    """Get current rate limit status for API endpoint"""
    return rate_limiter.get_status()

def parse_nl(text):
    """
    Parse natural language text into shell commands using Google Gemini API.
    Falls back to pattern matching if API fails.
    Returns list of command strings that can be executed sequentially.
    """
    
    # Enhanced fallback patterns for common multi-step operations
    low = text.lower().strip()
    
    # Handle "create a new file X and move it into Y" pattern
    if ('create' in low or 'make' in low) and 'file' in low and 'move' in low and 'into' in low:
        words = text.split()
        low_words = low.split()
        commands = []
        
        # Find file name - look for word after "file"
        file_name = None
        if 'file' in low_words:
            file_idx = low_words.index('file')
            # Check if there's a name after "file" and before "and"
            for i in range(file_idx + 1, len(words)):
                if low_words[i] == 'and':
                    break
                if not low_words[i] in ['a', 'new', 'called', 'named']:
                    file_name = words[i]
                    break
        
        # Find destination folder - look for word after "into"
        dest_folder = None
        if 'into' in low_words:
            into_idx = low_words.index('into')
            if into_idx + 1 < len(words):
                # Handle "into static folder" or "into static"
                dest_folder = words[into_idx + 1]
                # Remove "folder" if it's there
                if dest_folder == 'folder' and into_idx + 2 < len(words):
                    dest_folder = words[into_idx + 2]
                elif dest_folder.endswith('folder'):
                    dest_folder = dest_folder[:-6].strip()
        
        # Also check for "move it into X" pattern
        if 'move' in low_words and 'it' in low_words:
            move_idx = low_words.index('move')
            if move_idx + 1 < len(low_words) and low_words[move_idx + 1] == 'it':
                # The file to move is the one we just created
                pass  # file_name is already set from above
        
        if file_name and dest_folder:
            commands.append(f'touch {file_name}')
            commands.append(f'mv {file_name} {dest_folder}/')
            return commands
    
    # Handle "make a new folder X and move Y into it" pattern
    if ('make' in low or 'create' in low) and 'folder' in low and 'move' in low and 'into' in low:
        words = text.split()
        low_words = low.split()
        commands = []
        
        # Find folder name - look for word after "folder"
        folder_name = None
        if 'folder' in low_words:
            folder_idx = low_words.index('folder')
            # Check if there's a name after "folder" and before "and"
            for i in range(folder_idx + 1, len(words)):
                if low_words[i] == 'and':
                    break
                if not low_words[i] in ['a', 'new', 'called', 'named']:
                    folder_name = words[i]
                    break
        
        if folder_name:
            commands.append(f'mkdir {folder_name}')
            
            # Find file to move - look for word after "move"
            if 'move' in low_words:
                move_idx = low_words.index('move')
                if move_idx + 1 < len(words):
                    file_name = words[move_idx + 1]
                    commands.append(f'mv {file_name} {folder_name}/')
                    
        return commands if commands else fallback_simple_patterns(text)
    
    # Handle folder creation with "and" operations
    if 'create' in low and 'folder' in low and 'and' in low:
        return handle_multi_step_creation(text)
    
    # Single-step patterns
    return fallback_simple_patterns(text)

def handle_multi_step_creation(text):
    """Handle complex creation commands with multiple steps"""
    commands = []
    low = text.lower()
    
    # Extract folder name
    if 'called' in low or 'named' in low:
        words = text.split()
        low_words = low.split()
        
        # Find folder name
        folder_name = None
        if 'called' in low_words:
            called_idx = low_words.index('called')
            folder_name = words[called_idx + 1]
        elif 'named' in low_words:
            named_idx = low_words.index('named')
            folder_name = words[named_idx + 1]
            
        if folder_name:
            commands.append(f'mkdir {folder_name}')
            
            # Look for additional operations
            if 'move' in low and 'into' in low:
                # Find what to move
                move_idx = low_words.index('move')
                if move_idx + 1 < len(words):
                    file_name = words[move_idx + 1]
                    commands.append(f'mv {file_name} {folder_name}/')
                    
    return commands if commands else [text]  # Fallback to original text

def fallback_simple_patterns(text):
    """Handle simple single-step commands"""
    low = text.lower().strip()
    
    # Enhanced folder creation patterns
    if low.startswith('make new folder called ') or low.startswith('create new folder called '):
        name = text[len('make new folder called '):].strip() if 'make' in low else text[len('create new folder called '):].strip()
        return [f'mkdir {name}']
    elif low.startswith('make a new folder called ') or low.startswith('create a new folder called '):
        name = text[len('make a new folder called '):].strip() if 'make' in low else text[len('create a new folder called '):].strip()
        return [f'mkdir {name}']
    elif 'create a new folder' in low and 'called' in low:
        parts = text.split('called')
        if len(parts) > 1:
            name = parts[1].strip().split()[0]
            return [f'mkdir {name}']
    elif 'make a new folder' in low and 'called' in low:
        parts = text.split('called')
        if len(parts) > 1:
            name = parts[1].strip().split()[0]
            return [f'mkdir {name}']
    # Handle "create a new folder" without specific name
    elif low == 'create a new folder' or low == 'make a new folder':
        return [f'mkdir new_folder']
    # Handle "create folder X" pattern
    elif ('create folder' in low or 'make folder' in low) and len(text.split()) >= 3:
        words = text.split()
        # Find the word after "folder"
        for i, word in enumerate(words):
            if word.lower() == 'folder' and i + 1 < len(words):
                folder_name = words[i + 1]
                return [f'mkdir {folder_name}']
    
    # Clear screen patterns
    elif 'clear' in low and ('terminal' in low or 'screen' in low):
        return ['clear']
    elif low.strip() in ['clear', 'cls']:
        return ['clear']
    
    # File creation with content
    elif 'create a file' in low and 'write' in low:
        words = text.lower().split()
        try:
            # Find filename
            filename = 'newfile.txt'  # Default filename
            if 'named' in words:
                named_idx = words.index('named')
                filename = text.split()[named_idx + 1]
            elif 'called' in words:
                called_idx = words.index('called')
                filename = text.split()[called_idx + 1]
            
            # Extract content after "write" or "code"
            content = ""
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
            
            if content:
                return [f'write {filename} "{content}"']
            else:
                return [f'touch {filename}']
        except:
            return [f'touch newfile.txt']
    
    # File execution patterns
    elif 'execute' in low or 'run' in low:
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
    
    # File movement patterns
    elif 'move' in low and 'into' in low:
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
    
    # File listing patterns
    elif 'show' in low and 'python' in low and 'file' in low:
        return ['search *.py']
    elif 'show' in low and 'all' in low and 'file' in low:
        return ['ls -l']
    elif 'list' in low and 'python' in low:
        return ['search *.py']
    elif 'find' in low and 'python' in low:
        return ['search *.py']
    
    # If no patterns match, try AI parsing
    return try_ai_parsing(text)

def try_ai_parsing(text):
    """
    Use Google Gemini API to parse natural language commands.
    Returns list of shell commands or empty list if parsing fails.
    Includes rate limiting to prevent API quota exceeded errors.
    """
    # Load API key from .env
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return []
    
    # Check rate limiting before making API call
    if not rate_limiter.can_make_request():
        status = rate_limiter.get_status()
        print(f"⏳ Rate limit reached ({status['requests_made']}/{status['max_requests']}). Please wait {status['time_until_reset']:.1f} seconds.")
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
        "- search pattern (find files matching pattern, e.g., search *.py)\n"
        "- tree (show directory structure)\n"
        "- cpu, mem, ps (system info)\n\n"
        "CRITICAL RULES:\n"
        "1. Do NOT use pipes (|), grep, find, or any shell operators\n"
        "2. To find Python files, use: search *.py\n"
        "3. To show all files, use: ls -l\n"
        "4. For file filtering, use the search command\n"
        "5. Only return basic commands from the list above\n\n"
        f"User instruction: {text}\n"
        "Commands:"
    )
    
    try:
        # Record the API request for rate limiting
        rate_limiter.record_request()
        
        # Use GenerativeModel for Gemini with timeout and safety settings
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
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