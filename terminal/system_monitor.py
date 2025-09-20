import psutil


def cpu():
    """Return CPU usage percentage."""
    return f"CPU Usage: {psutil.cpu_percent(interval=1)}%"


def mem():
    """Return memory usage percentage."""
    mem = psutil.virtual_memory()
    return f"Memory Usage: {mem.percent}%"


def ps():
    """Return list of running processes."""
    output = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            info = proc.info
            output.append(f"{info['pid']}	{info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return '\n'.join(output)

SYS_COMMANDS = {
    'cpu': cpu,
    'mem': mem,
    'ps': ps,
}
