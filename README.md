# Python Terminal

A Python-based command terminal that mimics the behavior of a real system terminal.

## Setup

1. Navigate to the project directory:
   ```powershell
   cd c:\code\codemate\python_terminal
   ```
2. Create a `.env` file at the root with your Gemini API key:
   ```text
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### CLI Mode

Run the terminal in CLI mode (default):
```powershell
python main.py --mode cli
```

Type commands at the `> ` prompt. Supported commands:

- File and directory operations:
  - `ls [path]` – list files and directories
  - `pwd` – print current working directory
  - `cd <path>` – change directory
  - `mkdir <dir>` – create new directories
  - `rm <path>` – remove files/directories
  - `cat <file>` – read and display file contents
  - `touch <file>` – create empty files
- System monitoring:
  - `cpu` – show current CPU usage
  - `mem` – show memory usage
  - `ps` – list running processes
- `exit` – exit the terminal

Additional features:
- **AI parsing:** Set `OPENAI_API_KEY` and enter natural language instructions; AI will convert them to shell commands.
- **Autocomplete:** Press Tab to autocomplete command names or file paths.

Navigation with Up/Down arrow keys to traverse command history is supported.

Additional feature:
- **AI parsing via Gemini:** Ensure `GEMINI_API_KEY` is set; type natural language instructions to invoke Gemini-2.5-Flash model.

### Web Mode (Optional)

Run a minimal web-based terminal:
```powershell
python main.py --mode web
```

Then open your browser to `http://127.0.0.1:5000` to access the terminal interface.

> **Note:** Add an `index.html` template under `templates/` to provide a frontend UI.

## Extensibility

Commands are modular functions located in `terminal/commands.py` and `terminal/system_monitor.py`. To add a new command, implement the function and register it in the `COMMANDS` or `SYS_COMMANDS` dictionary.

## AI Natural Language Interface (Optional)

Basic AI parser is included. To enable, set the `GEMINI_API_KEY` environment variable with your Gemini key. Natural language instructions like:

```powershell
create a folder named demo and a file test.txt inside it
```

will be converted to corresponding shell commands by the AI parser.

## License

MIT License
