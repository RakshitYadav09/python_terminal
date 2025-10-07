import argparse
from terminal.shell import Shell


def main():
    parser = argparse.ArgumentParser(description="Python Terminal")
    parser.add_argument(
        '--mode', choices=['cli', 'web'], default='cli', help='Interface mode: cli or web'
    )
    args = parser.parse_args()

    shell = Shell()
    if args.mode == 'cli':
        shell.run()
    else:
        try:
            import os
            from flask import Flask, request, jsonify, render_template
        except ImportError:
            print("Flask is not installed. Please install Flask or use CLI mode.")
            return

        base_dir = os.path.dirname(__file__)
        app = Flask(
            __name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static')
        )

        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/execute', methods=['POST'])
        def execute():
            data = request.get_json() or {}
            command = data.get('command', '')
            
            # Set a flag to indicate we're in web mode
            import os
            os.environ['TERMINAL_MODE'] = 'web'
            
            output = shell.run_command(command)
            
            # Clean up ANSI escape codes for web display
            import re
            # Remove ANSI escape sequences
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            clean_output = ansi_escape.sub('', output)
            
            cwd = os.getcwd()
            return jsonify({'output': clean_output, 'cwd': cwd})

        @app.route('/cwd', methods=['GET'])
        def get_cwd():
            return jsonify({'cwd': os.getcwd()})

        @app.route('/rate-limit', methods=['GET'])
        def get_rate_limit():
            from terminal.ai_parser import get_rate_limit_status
            status = get_rate_limit_status()
            return jsonify(status)
        
        # Production configuration for hosting platforms like Render
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'  # Bind to all interfaces for external access
        debug_mode = os.environ.get('FLASK_ENV') != 'production'
        
        print(f"Starting Flask app on {host}:{port}")
        app.run(host=host, port=port, debug=debug_mode)


if __name__ == '__main__':
    main()
