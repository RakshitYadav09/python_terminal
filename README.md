# Python Terminal 🐍

A modern, feature-rich terminal emulator built entirely in Python. This project started as a simple command-line tool but evolved into something much cooler - a web-based terminal with AI integration!

## What This Project Does

Ever wanted to build your own terminal? This project gives you both a traditional command-line interface AND a sleek web interface that runs in your browser. Plus, it has AI integration so you can type natural language commands like "show me all python files" and it actually understands what you want!

## Features That Actually Work

### Core Terminal Commands
- **File Operations**: `ls`, `cat`, `touch`, `mkdir`, `rm`, `mv`
- **Navigation**: `pwd`, `cd` with proper path handling
- **Text Processing**: `echo`, `write` for creating files with content
- **Python Execution**: Run Python scripts directly from the terminal

### System Monitoring
- **CPU Usage**: Real-time CPU monitoring with `cpu` command
- **Memory Stats**: Check memory usage with `mem` command
- **Process List**: See running processes with `ps` command
- **System Info**: Complete system overview with `sysinfo`

### Advanced Features
- **Directory Tree View**: Visual file structure with `tree` command
- **File Search**: Find files by pattern with `search` command
- **Command History**: Navigate through previous commands
- **AI Natural Language**: Type commands in plain English!

### Dual Interface
- **CLI Mode**: Traditional terminal experience
- **Web Mode**: Modern browser-based interface with clickable command chips

## Quick Start

### Prerequisites
```bash
Python 3.8+
Flask (for web mode)
```

### Installation
1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your AI integration (optional):
   - Get a free API key from Google AI Studio
   - Create a `.env` file in the project root
   - Add: `GEMINI_API_KEY=your_key_here`

### Running the Terminal

**Command Line Mode:**
```bash
python main.py --mode cli
```

**Web Interface Mode:**
```bash
python main.py --mode web
```
Then open your browser to `http://localhost:5000`

## Usage Examples

### Basic Commands
```bash
# List files with details
ls -l

# Create a new directory
mkdir my_folder

# Write content to a file
echo "Hello World" > greeting.txt

# View file contents
cat greeting.txt

# Check system resources
cpu
mem
sysinfo
```

### AI-Powered Commands
The coolest feature - just type what you want in natural language:
```bash
# These all work!
show me all python files
create a new folder called projects
what files are in this directory
check memory usage
run hello.py
```

### Web Interface
The web version includes:
- Clickable command suggestions
- Real-time command execution
- Clean, modern interface
- Command history navigation
- Status indicators

## Project Structure

```
python_terminal/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (don't commit this!)
├── .gitignore            # Git ignore rules
│
├── terminal/             # Core terminal logic
│   ├── shell.py         # Main shell implementation
│   ├── commands.py      # All terminal commands
│   ├── ai_parser.py     # Natural language processing
│   └── system_monitor.py # System monitoring functions
│
├── templates/           # Web interface templates
│   └── index.html      # Main web page
│
├── static/             # Web assets
│   ├── style.css      # Styling for web interface
│   └── terminal.js    # Client-side JavaScript
│
└── utils/              # Helper utilities
    ├── error_handler.py # Error handling
    └── helpers.py      # Utility functions
```

## Technical Details

### Architecture
- **Shell Engine**: Custom shell implementation using Python's `cmd` module
- **Command System**: Modular command structure for easy extension
- **Web Framework**: Flask for the web interface
- **AI Integration**: Google Gemini API for natural language processing
- **Cross-Platform**: Works on Windows, macOS, and Linux

### How It Works
1. **CLI Mode**: Direct terminal interaction using Python's cmd module
2. **Web Mode**: Flask server serves a web interface that communicates via AJAX
3. **AI Processing**: Natural language commands are parsed and converted to terminal commands
4. **Command Execution**: All commands are executed in a sandboxed environment

## Deployment

### Local Development
Just run `python main.py --mode web` and you're good to go!

### Cloud Deployment
Works great on platforms like:
- **Render**: Set start command to `python main.py --mode web`
- **Heroku**: Includes Procfile for easy deployment
- **Railway**: One-click deployment from GitHub
- **PythonAnywhere**: Upload and configure as web app

Remember to set your `GEMINI_API_KEY` environment variable on your hosting platform!

## Contributing

Found a bug? Want to add a feature? Here's how:

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly (both CLI and web modes)
5. Submit a pull request

### Adding New Commands
Commands are defined in `terminal/commands.py`. Just add a new function and register it in the `COMMANDS` dictionary. Easy!

## Troubleshooting

**"ImportError: attempted relative import"**
- Make sure you're running from the project root
- Use `python main.py` not `python terminal/shell.py`

**"Flask not found"**
- Install requirements: `pip install -r requirements.txt`

**Web interface not loading**
- Check if port 5000 is available
- Try a different port: `export PORT=8080` then run

**AI commands not working**
- Check your `.env` file has the correct API key
- Verify internet connection
- API key might need regeneration

## License

This project is open source. Feel free to use it, modify it, learn from it!

## Why I Built This

Started as a simple assignment but became a passion project. Wanted to understand how terminals actually work under the hood, and the web interface was just for fun. The AI integration came later when I realized how cool it would be to have a terminal that understands natural language.

Hope you find it useful or at least interesting! 🚀