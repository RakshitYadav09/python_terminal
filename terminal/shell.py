import os
import shlex
import io
from cmd import Cmd
from colorama import init, Fore, Style
from .commands import COMMANDS
from .system_monitor import SYS_COMMANDS
from .ai_parser import parse_nl

# Initialize colorama
init(autoreset=True)

class Shell(Cmd):
    intro = f"""{Fore.GREEN}
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗                    ║
║   ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║                    ║
║   ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║                    ║
║   ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║                    ║
║   ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║                    ║
║   ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                    ║
║                                                                            ║
║                 ████████╗███████╗██████╗ ███╗   ███╗                       ║
║                 ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║                       ║
║                    ██║   █████╗  ██████╔╝██╔████╔██║                       ║
║                    ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║                       ║
║                    ██║   ███████╗██║  ██║██║ ╚═╝ ██║                       ║
║                    ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝                       ║
║                                                                            ║
║                                                                            ║
║                                                                            ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
{Fore.CYAN}>> SYSTEM INITIALIZED{Style.RESET_ALL}
{Fore.YELLOW}>> TYPE 'help' FOR COMMAND LIST{Style.RESET_ALL}
{Fore.MAGENTA}>> AI MODE: try "show me all files"{Style.RESET_ALL}
{Fore.GREEN}>> LOGGING: .terminal_history{Style.RESET_ALL}

"""
    prompt = f'{Fore.GREEN}[{Fore.CYAN}TERM{Fore.GREEN}]{Fore.YELLOW}> {Style.RESET_ALL}'

    def __init__(self):
        super().__init__()
        try:
            import readline
            readline.set_completer(self.complete)
            readline.parse_and_bind('tab: complete')
        except ImportError:
            pass

    # Help methods for individual commands - these make the help system work properly
    def help_ls(self):
        self.stdout.write("ls [-l] [path] - List directory contents\n")
        self.stdout.write("  -l: Show detailed listing with file sizes and dates\n")
        self.stdout.write("  Examples: ls, ls -l, ls /home\n")

    def help_pwd(self):
        print("pwd - Print current working directory")
        print("  Shows the full path of your current location")

    def help_cd(self):
        print("cd <directory> - Change to specified directory")
        print("  Examples: cd /home, cd .., cd subfolder")

    def help_mkdir(self):
        print("mkdir <directory> - Create new directory")
        print("  Examples: mkdir newfolder, mkdir 'folder with spaces'")

    def help_rm(self):
        print("rm <file/directory> - Remove files or directories")
        print("  Use with caution! This permanently deletes files")
        print("  Examples: rm file.txt, rm -rf folder")

    def help_cat(self):
        print("cat <file> - Display file contents")
        print("  Examples: cat readme.txt, cat /path/to/file")

    def help_touch(self):
        print("touch <file> - Create empty file")
        print("  Examples: touch newfile.txt, touch script.py")

    def help_mv(self):
        print("mv <source> <destination> - Move or rename files")
        print("  Examples: mv old.txt new.txt, mv file.txt folder/")

    def help_echo(self):
        self.stdout.write("echo <text> [> file] - Print text or write to file\n")
        self.stdout.write("  Examples: echo 'Hello World', echo 'text' > file.txt\n")

    def help_write(self):
        print("write <file> <content> - Write content to file")
        print("  Examples: write test.txt 'Hello World'")

    def help_tree(self):
        print("tree - Display directory structure as tree")
        print("  Shows files and folders in a visual tree format")

    def help_search(self):
        print("search <pattern> - Search for files matching pattern")
        print("  Examples: search '*.py', search 'test*'")

    def help_cpu(self):
        print("cpu - Show current CPU usage percentage")

    def help_mem(self):
        print("mem - Show current memory usage")

    def help_ps(self):
        print("ps - List currently running processes")

    def help_sysinfo(self):
        print("sysinfo - Display comprehensive system information")

    def help_history(self):
        print("history [count] - Show command history")
        print("  Examples: history, history 10")

    def help_clear(self):
        self.stdout.write("clear - Clear the terminal screen\n")

    def help_python(self):
        print("python <script> - Execute Python script")
        print("  Examples: python script.py, python test.py")

    def help_run(self):
        print("run <script> - Execute Python script (alias for python)")
        print("  Examples: run script.py, run test.py")

    def default(self, line: str):
        from .commands import log_command
        
        line = line.strip()
        if not line:
            return
        if line == 'exit':
            log_command("exit")
            return True
        
        # Log the original command
        log_command(line)
        
        # Try parsing as direct command first
        parts = shlex.split(line)
        cmd_name = parts[0]
        cmd_args = parts[1:]
        
        # Execute known commands directly
        if cmd_name in COMMANDS:
            try:
                output = COMMANDS[cmd_name](cmd_args)
                if output:
                    self.stdout.write(output + '\n')
            except Exception as e:
                self.stdout.write(f'{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n')
            return
        elif cmd_name in SYS_COMMANDS:
            try:
                output = SYS_COMMANDS[cmd_name]()
                if output:
                    self.stdout.write(output + '\n')
            except Exception as e:
                self.stdout.write(f'{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n')
            return
        
        # If not a known command, try AI parsing
        try:
            self.stdout.write(f"{Fore.YELLOW}🤖 AI Thinking... {Style.RESET_ALL}")
            self.stdout.flush()
            commands = parse_nl(line)
            
            if commands:
                self.stdout.write(f"\r{Fore.CYAN}🧠 AI interpreted: {' && '.join(commands)}{Style.RESET_ALL}\n")
                for i, cmd in enumerate(commands):
                    self.stdout.write(f"{Fore.BLUE}⚡ Executing ({i+1}/{len(commands)}): {cmd}{Style.RESET_ALL}\n")
                    self.execute_single_command(cmd)
            else:
                self.stdout.write(f"\r{Fore.RED}❓ Unknown command: {cmd_name}{Style.RESET_ALL}\n")
        except KeyboardInterrupt:
            self.stdout.write(f"\r{Fore.YELLOW}⏹️ AI parsing cancelled.{Style.RESET_ALL}\n")
        except Exception as e:
            self.stdout.write(f"\r{Fore.RED}🔥 AI parsing error: {e}{Style.RESET_ALL}\n")
            self.stdout.write(f"{Fore.RED}❓ Unknown command: {cmd_name}{Style.RESET_ALL}\n")
    
    def execute_single_command(self, cmd_str: str):
        """Execute a single command without AI parsing to avoid recursion"""
        try:
            parts = shlex.split(cmd_str.strip())
            if not parts:
                return
                
            cmd_name = parts[0]
            cmd_args = parts[1:]
            
            if cmd_name in COMMANDS:
                try:
                    output = COMMANDS[cmd_name](cmd_args)
                    if output:
                        self.stdout.write(output + '\n')
                except Exception as e:
                    self.stdout.write(f'{Fore.RED}❌ Error in {cmd_name}: {e}{Style.RESET_ALL}\n')
            elif cmd_name in SYS_COMMANDS:
                try:
                    output = SYS_COMMANDS[cmd_name]()
                    if output:
                        self.stdout.write(output + '\n')
                except Exception as e:
                    self.stdout.write(f'Error in {cmd_name}: {e}\n')
            else:
                self.stdout.write(f'Unknown command: {cmd_name}\n')
        except Exception as e:
            self.stdout.write(f'Command execution error: {e}\n')
    
    # Autocomplete for commands and file paths
    def complete(self, text, state):
        import readline
        buffer = readline.get_line_buffer()
        line = buffer.strip().split()
        # Completing command names
        if len(line) <= 1:
            options = list(COMMANDS.keys()) + list(SYS_COMMANDS.keys()) + ['exit']
            matches = [c for c in options if c.startswith(text)]
        else:
            # Complete file system paths
            import glob
            pattern = text + '*'
            matches = glob.glob(pattern)
        try:
            return matches[state]
        except IndexError:
            return None

    def run(self):
        self.cmdloop()

    def run_command(self, cmd_str: str) -> str:
        buffer = io.StringIO()
        old_stdout = self.stdout
        self.stdout = buffer
        try:
            self.onecmd(cmd_str)
        finally:
            self.stdout = old_stdout
        return buffer.getvalue().strip()
