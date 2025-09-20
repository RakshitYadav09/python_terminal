import os
import shutil
import sys
import psutil
from colorama import init, Fore, Back, Style
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
import platform
import time

# Initialize colorama for cross-platform color support
init(autoreset=True)
console = Console()


def get_file_type_icon(path):
    """Get retro ASCII icon based on file type"""
    if os.path.isdir(path):
        return "[DIR]"
    ext = os.path.splitext(path)[1].lower()
    icon_map = {
        '.py': '[PY]', '.js': '[JS]', '.html': '[HTM]', '.css': '[CSS]',
        '.txt': '[TXT]', '.md': '[MD]', '.json': '[JSN]', '.csv': '[CSV]',
        '.jpg': '[IMG]', '.png': '[IMG]', '.gif': '[IMG]', '.mp4': '[VID]',
        '.mp3': '[AUD]', '.pdf': '[PDF]', '.zip': '[ZIP]', '.exe': '[EXE]'
    }
    return icon_map.get(ext, '[---]')

def format_file_size(size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"

def add_loading_animation(duration=2):
    """Show retro loading animation"""
    chars = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for char in chars:
            if time.time() >= end_time:
                break
            print(f"\r[{char}] PROCESSING...", end="", flush=True)
            time.sleep(0.2)
    print("\r" + " " * 20 + "\r", end="")  # Clear loading line

def log_command(command):
    """Log executed command to history file"""
    try:
        with open('.terminal_history', 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {command}\n")
    except Exception:
        pass  # Silently ignore logging errors


def ls(args):
    # Log command
    log_command(f"ls {' '.join(args)}")
    
    # Check if we're in web mode
    import os
    is_web_mode = os.environ.get('TERMINAL_MODE') == 'web'
    
    # Parse flags and path
    show_all = False
    long_format = False
    path = '.'
    
    for arg in args:
        if arg.startswith('-'):
            if 'a' in arg:
                show_all = True
            if 'l' in arg:
                long_format = True
        else:
            path = arg
    
    try:
        items = os.listdir(path)
        if not show_all:
            items = [item for item in items if not item.startswith('.')]
        
        if long_format:
            if is_web_mode:
                # Simple table format for web
                result = f"Directory: {os.path.abspath(path)}\n\n"
                result += f"{'Type':<8} {'Name':<25} {'Size':<12} {'Modified':<20}\n"
                result += "=" * 65 + "\n"
                
                for item in sorted(items):
                    item_path = os.path.join(path, item)
                    try:
                        stat_info = os.stat(item_path)
                        mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat_info.st_mtime))
                        
                        if os.path.isdir(item_path):
                            result += f"{'[DIR]':<8} {item:<25} {'-':<12} {mod_time:<20}\n"
                        else:
                            ext = os.path.splitext(item)[1][1:].upper() or 'FILE'
                            size = format_file_size(stat_info.st_size)
                            result += f"{'[' + ext + ']':<8} {item:<25} {size:<12} {mod_time:<20}\n"
                    except Exception:
                        result += f"{'[UNK]':<8} {item:<25} {'Unknown':<12} {'Unknown':<20}\n"
                
                return result
            else:
                # Rich table for CLI
                table = Table(title=f">> DIRECTORY: {os.path.abspath(path)}")
                table.add_column("TYPE", style="cyan", no_wrap=True)
                table.add_column("NAME", style="green")
                table.add_column("SIZE", style="yellow", justify="right")
                table.add_column("MODIFIED", style="magenta")
                
                for item in sorted(items):
                    item_path = os.path.join(path, item)
                    try:
                        stat_info = os.stat(item_path)
                        mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat_info.st_mtime))
                        
                        if os.path.isdir(item_path):
                            table.add_row("[DIR]", item, "-", mod_time)
                        else:
                            icon = get_file_type_icon(item_path)
                            size = format_file_size(stat_info.st_size)
                            table.add_row(icon, item, size, mod_time)
                    except Exception:
                        table.add_row("[???]", item, "UNKNOWN", "UNKNOWN")
                
                with console.capture() as capture:
                    console.print(table)
                return capture.get()
        else:
            # Simple listing for both web and CLI
            result = []
            for item in sorted(items):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    if is_web_mode:
                        result.append(f"[DIR]  {item}/")
                    else:
                        result.append(f">> {item}/")
                else:
                    ext = os.path.splitext(item)[1] or ''
                    if is_web_mode:
                        result.append(f"[FILE] {item}")
                    else:
                        result.append(f"   {item}")
            return '\n'.join(result)
    except Exception as e:
        return f"Error: {e}"


def pwd(args):
    log_command("pwd")
    current_path = os.getcwd()
    is_web_mode = os.environ.get('TERMINAL_MODE') == 'web'
    
    if is_web_mode:
        return f"Current directory: {current_path}"
    else:
        return f"{Fore.CYAN}>> CURRENT PATH: {current_path}{Style.RESET_ALL}"


def cd(args):
    log_command(f"cd {' '.join(args)}")
    if not args:
        return f"{Fore.RED}[ERROR] cd: missing operand{Style.RESET_ALL}"
    try:
        os.chdir(args[0])
        return f"{Fore.GREEN}[OK] Changed to: {os.getcwd()}{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.RED}[ERROR] cd: {e}{Style.RESET_ALL}"


def mkdir(args):
    log_command(f"mkdir {' '.join(args)}")
    if not args:
        return f"{Fore.RED}[ERROR] mkdir: missing operand{Style.RESET_ALL}"
    try:
        os.makedirs(args[0], exist_ok=True)
        return f"{Fore.GREEN}[OK] Directory '{args[0]}' created{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.RED}[ERROR] mkdir: {e}{Style.RESET_ALL}"


def rm(args):
    if not args:
        return f"{Fore.RED}rm: missing operand{Style.RESET_ALL}"
    
    # Parse flags and paths
    recursive = False
    force = False
    paths = []
    
    for arg in args:
        if arg.startswith('-'):
            if 'r' in arg or 'R' in arg:
                recursive = True
            if 'f' in arg:
                force = True
        else:
            paths.append(arg)
    
    if not paths:
        return f"{Fore.RED}rm: missing operand{Style.RESET_ALL}"
    
    results = []
    for path in paths:
        try:
            if os.path.isdir(path):
                if not force:
                    # Ask for confirmation
                    print(f"{Fore.YELLOW}⚠️  Delete directory '{path}' and all contents? (y/N): {Style.RESET_ALL}", end='')
                    try:
                        response = input().lower()
                        if response != 'y':
                            results.append(f"{Fore.YELLOW}❌ Cancelled deletion of '{path}'{Style.RESET_ALL}")
                            continue
                    except:
                        results.append(f"{Fore.YELLOW}❌ Cancelled deletion of '{path}'{Style.RESET_ALL}")
                        continue
                
                if recursive:
                    shutil.rmtree(path)
                    results.append(f"{Fore.GREEN}✅ Directory '{path}' deleted{Style.RESET_ALL}")
                else:
                    try:
                        os.rmdir(path)  # Only works if empty
                        results.append(f"{Fore.GREEN}✅ Directory '{path}' deleted{Style.RESET_ALL}")
                    except OSError:
                        results.append(f"{Fore.RED}rm: cannot remove '{path}': Directory not empty (use -r){Style.RESET_ALL}")
            elif os.path.isfile(path):
                os.remove(path)
                results.append(f"{Fore.GREEN}✅ File '{path}' deleted{Style.RESET_ALL}")
            else:
                if not force:
                    results.append(f"{Fore.RED}rm: cannot remove '{path}': No such file or directory{Style.RESET_ALL}")
        except Exception as e:
            if not force:
                results.append(f"{Fore.RED}rm: {e}{Style.RESET_ALL}")
    
    return '\n'.join(results)


def cat(args):
    if not args:
        raise ValueError("cat: missing operand")
    with open(args[0], 'r') as f:
        return f.read()


def mv(args):
    if len(args) < 2:
        raise ValueError("mv: missing operand")
    src, dst = args[0], args[1]
    shutil.move(src, dst)


def touch(args):
    if not args:
        raise ValueError("touch: missing operand")
    path = args[0]
    open(path, 'a').close()
    os.utime(path, None)


def echo(args):
    """Echo text to stdout or redirect to file"""
    if not args:
        return ""
    
    text = " ".join(args)
    
    # Handle redirection: echo "text" > file.txt
    if ">" in args:
        redirect_idx = args.index(">")
        if redirect_idx < len(args) - 1:
            filename = args[redirect_idx + 1]
            content = " ".join(args[:redirect_idx])
            # Remove quotes if present
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            elif content.startswith("'") and content.endswith("'"):
                content = content[1:-1]
            
            with open(filename, 'w') as f:
                f.write(content)
            return f"Content written to {filename}"
        else:
            raise ValueError("echo: missing filename after >")
    
    # Handle append redirection: echo "text" >> file.txt
    elif ">>" in args:
        redirect_idx = args.index(">>")
        if redirect_idx < len(args) - 1:
            filename = args[redirect_idx + 1]
            content = " ".join(args[:redirect_idx])
            # Remove quotes if present
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            elif content.startswith("'") and content.endswith("'"):
                content = content[1:-1]
            
            with open(filename, 'a') as f:
                f.write(content + '\n')
            return f"Content appended to {filename}"
        else:
            raise ValueError("echo: missing filename after >>")
    
    # Regular echo
    return text


def python_exec(args):
    """Execute Python files"""
    if not args:
        raise ValueError("python: missing script name")
    
    script = args[0]
    if not script.endswith('.py'):
        script += '.py'
    
    if not os.path.exists(script):
        raise ValueError(f"python: can't open file '{script}': No such file or directory")
    
    import subprocess
    import sys
    
    try:
        result = subprocess.run([sys.executable, script], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"Error: {result.stderr}"
        
        return output.strip() if output else f"Script {script} executed successfully"
    
    except subprocess.TimeoutExpired:
        raise ValueError(f"python: script '{script}' timed out")
    except Exception as e:
        raise ValueError(f"python: execution error: {e}")


def clear(args):
    """Clear the terminal screen"""
    import os
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS
        os.system('clear')
    return ""


def help_cmd(args):
    """Show available commands"""
    commands = {
        'ls': 'List directory contents',
        'pwd': 'Print working directory', 
        'cd': 'Change directory',
        'mkdir': 'Create directory',
        'rm': 'Remove files/directories',
        'cat': 'Display file contents',
        'touch': 'Create empty file',
        'mv': 'Move/rename files',
        'echo': 'Print text or write to file',
        'write': 'Write content to file',
        'python': 'Execute Python scripts',
        'clear': 'Clear screen',
        'cpu': 'Show CPU usage',
        'mem': 'Show memory usage', 
        'ps': 'List processes',
        'exit': 'Exit terminal'
    }
    
    result = "Available commands:\n"
    for cmd, desc in commands.items():
        result += f"  {cmd:<8} - {desc}\n"
    
    return result


def python_exec(args):
    """Execute a Python file"""
    if not args:
        raise ValueError("python: missing filename")
    
    filename = args[0]
    
    if not os.path.exists(filename):
        raise ValueError(f"python: cannot execute '{filename}': No such file")
    
    if not filename.endswith('.py'):
        raise ValueError(f"python: '{filename}' is not a Python file")
    
    import subprocess
    import sys
    
    try:
        result = subprocess.run([sys.executable, filename], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.getcwd())
        
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"Error: {result.stderr}"
        
        return output.strip() if output else "Program executed successfully"
        
    except Exception as e:
        raise ValueError(f"python: execution failed: {e}")


def run(args):
    """Run a file (alias for python command for .py files)"""
    if not args:
        raise ValueError("run: missing filename")
    
    filename = args[0]
    
    if filename.endswith('.py'):
        return python_exec(args)
    else:
        raise ValueError(f"run: unsupported file type '{filename}'")


def write_file(args):
    """Write content to file: write filename "content" """
    if len(args) < 2:
        raise ValueError("write: usage: write filename \"content\"")
    
    filename = args[0]
    content = " ".join(args[1:])
    
    # Remove quotes if present
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
    elif content.startswith("'") and content.endswith("'"):
        content = content[1:-1]
    
    # Handle escape sequences
    content = content.replace('\\n', '\n').replace('\\t', '\t')
    
    with open(filename, 'w') as f:
        f.write(content)
    
    return f"Content written to {filename}"


def clear(args):
    """Clear the terminal screen (for CLI mode only)"""
    # For CLI mode, print enough newlines to clear screen
    return f"{Fore.GREEN}🧹 Screen cleared{Style.RESET_ALL}\n" + "\n" * 30


def tree(args):
    """Print a tree view of files & folders"""
    path = args[0] if args else '.'
    
    try:
        tree_view = Tree(f"📁 {os.path.abspath(path)}")
        
        def add_tree_items(tree_node, dir_path, max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            try:
                items = sorted(os.listdir(dir_path))
                for item in items:
                    if item.startswith('.'):
                        continue
                    item_path = os.path.join(dir_path, item)
                    if os.path.isdir(item_path):
                        branch = tree_node.add(f"📁 {item}")
                        add_tree_items(branch, item_path, max_depth, current_depth + 1)
                    else:
                        tree_node.add(f"📄 {item}")
            except PermissionError:
                tree_node.add("❌ Permission denied")
        
        add_tree_items(tree_view, path)
        
        with console.capture() as capture:
            console.print(tree_view)
        return capture.get()
        
    except Exception as e:
        return f"{Fore.RED}tree: {e}{Style.RESET_ALL}"


def search(args):
    """Search filenames matching a pattern"""
    if not args:
        return f"{Fore.RED}search: missing search pattern{Style.RESET_ALL}"
    
    pattern = args[0].lower()
    path = args[1] if len(args) > 1 else '.'
    
    try:
        matches = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if pattern in file.lower():
                    full_path = os.path.join(root, file)
                    matches.append(f"{Fore.GREEN}📄 {full_path}{Style.RESET_ALL}")
            for dir in dirs:
                if pattern in dir.lower():
                    full_path = os.path.join(root, dir)
                    matches.append(f"{Fore.BLUE}📁 {full_path}/{Style.RESET_ALL}")
        
        if matches:
            return f"{Fore.CYAN}🔍 Found {len(matches)} matches:\n{Style.RESET_ALL}" + '\n'.join(matches)
        else:
            return f"{Fore.YELLOW}🔍 No matches found for '{pattern}'{Style.RESET_ALL}"
            
    except Exception as e:
        return f"{Fore.RED}search: {e}{Style.RESET_ALL}"


def sysinfo(args):
    """Show OS, Python version, uptime"""
    try:
        import sys
        import psutil
        
        table = Table(title="🖥️ System Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        # Basic system info
        table.add_row("Operating System", platform.platform())
        table.add_row("Architecture", platform.architecture()[0])
        table.add_row("Processor", platform.processor() or "Unknown")
        table.add_row("Python Version", sys.version.split()[0])
        table.add_row("Current Directory", os.getcwd())
        
        # System stats
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        uptime_str = f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m"
        table.add_row("Uptime", uptime_str)
        
        memory = psutil.virtual_memory()
        table.add_row("Total Memory", f"{memory.total // (1024**3)} GB")
        table.add_row("Available Memory", f"{memory.available // (1024**3)} GB")
        table.add_row("CPU Cores", str(psutil.cpu_count()))
        
        with console.capture() as capture:
            console.print(table)
        return capture.get()
        
    except Exception as e:
        return f"{Fore.RED}❌ sysinfo: {e}{Style.RESET_ALL}"


def history_cmd(args):
    """Show command history"""
    log_command("history")
    try:
        if not os.path.exists('.terminal_history'):
            return f"{Fore.YELLOW}📜 No command history found{Style.RESET_ALL}"
        
        table = Table(title="📜 Command History")
        table.add_column("Time", style="cyan")
        table.add_column("Command", style="green")
        
        with open('.terminal_history', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Show last 20 commands by default
        limit = 20
        if args and args[0].isdigit():
            limit = int(args[0])
            
        for line in lines[-limit:]:
            if line.strip():
                parts = line.strip().split('] ', 1)
                if len(parts) == 2:
                    timestamp = parts[0].replace('[', '')
                    command = parts[1]
                    table.add_row(timestamp, command)
        
        with console.capture() as capture:
            console.print(table)
        return capture.get()
        
    except Exception as e:
        return f"{Fore.RED}❌ Error reading history: {e}{Style.RESET_ALL}"


def help_cmd(args):
    """Show available commands"""
    from .system_monitor import SYS_COMMANDS
    is_web_mode = os.environ.get('TERMINAL_MODE') == 'web'
    
    if is_web_mode:
        # Simple text format for web
        result = "AVAILABLE COMMANDS\n"
        result += "=" * 50 + "\n\n"
        
        result += "FILE OPERATIONS:\n"
        result += "  ls           - List directory contents (ls -l for details)\n"
        result += "  pwd          - Print working directory\n"
        result += "  cd <dir>     - Change directory\n"
        result += "  mkdir <dir>  - Create directory\n"
        result += "  rm <file>    - Remove files/directories\n"
        result += "  cat <file>   - Display file contents\n"
        result += "  touch <file> - Create empty file\n"
        result += "  mv <src> <dst> - Move/rename files\n\n"
        
        result += "TEXT OPERATIONS:\n"
        result += "  echo <text>  - Print text or write to file\n"
        result += "  write <file> <content> - Write content to file\n\n"
        
        result += "PYTHON EXECUTION:\n"
        result += "  python <script> - Execute Python scripts\n"
        result += "  run <script>    - Run Python files\n\n"
        
        result += "SYSTEM MONITORING:\n"
        result += "  cpu        - Show CPU usage\n"
        result += "  mem        - Show memory usage\n"
        result += "  ps         - List processes\n"
        result += "  sysinfo    - Show system information\n\n"
        
        result += "UTILITIES:\n"
        result += "  tree       - Show directory tree\n"
        result += "  search <pattern> - Search for files\n"
        result += "  history    - Show command history\n"
        result += "  clear      - Clear screen\n"
        result += "  help       - Show this help\n"
        result += "  exit       - Exit terminal\n"
        
        return result
    else:
        # Rich table for CLI
        table = Table(title=">> AVAILABLE COMMANDS")
        table.add_column("COMMAND", style="cyan", no_wrap=True)
        table.add_column("DESCRIPTION", style="green")
        table.add_column("EXAMPLE", style="yellow")
        
        # File operations
        table.add_row("[bold cyan]FILE OPERATIONS[/bold cyan]", "", "")
        table.add_row("ls", "List directory contents", "ls -l")
        table.add_row("pwd", "Print working directory", "pwd")
        table.add_row("cd", "Change directory", "cd folder")
        table.add_row("mkdir", "Create directory", "mkdir newfolder")
        table.add_row("rm", "Remove files/directories", "rm -rf folder")
        table.add_row("cat", "Display file contents", "cat file.txt")
        table.add_row("touch", "Create empty file", "touch newfile.txt")
        table.add_row("mv", "Move/rename files", "mv old.txt new.txt")
        
        # Text operations
        table.add_row("[bold cyan]TEXT OPERATIONS[/bold cyan]", "", "")
        table.add_row("echo", "Print text or write to file", "echo 'hi' > file.txt")
        table.add_row("write", "Write content to file", "write file.txt 'content'")
        
        # Python execution
        table.add_row("[bold cyan]PYTHON EXECUTION[/bold cyan]", "", "")
        table.add_row("python", "Execute Python scripts", "python script.py")
        table.add_row("run", "Run Python files", "run script.py")
        
        # System monitoring
        table.add_row("[bold cyan]SYSTEM MONITORING[/bold cyan]", "", "")
        table.add_row("cpu", "Show CPU usage", "cpu")
        table.add_row("mem", "Show memory usage", "mem")
        table.add_row("ps", "List processes", "ps")
        table.add_row("sysinfo", "Show system information", "sysinfo")
        
        # Utilities
        table.add_row("[bold cyan]UTILITIES[/bold cyan]", "", "")
        table.add_row("tree", "Show directory tree", "tree")
        table.add_row("search", "Search for files", "search pattern")
        table.add_row("history", "Show command history", "history 10")
        table.add_row("clear", "Clear screen", "clear")
        table.add_row("help", "Show this help", "help")
        table.add_row("exit", "Exit terminal", "exit")
        
        with console.capture() as capture:
            console.print(table)
        return capture.get()


COMMANDS = {
    'ls': ls,
    'pwd': pwd,
    'cd': cd,
    'mkdir': mkdir,
    'rm': rm,
    'cat': cat,
    'touch': touch,
    'mv': mv,
    'echo': echo,
    'write': write_file,
    'python': python_exec,
    'run': run,
    'execute': run,  # alias for run
    'tree': tree,
    'search': search,
    'sysinfo': sysinfo,
    'history': history_cmd,
    'clear': clear,
    'help': help_cmd,
}
