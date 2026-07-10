import datetime

class Logger:
    """
    A simple logger that writes messages to a file with a timestamp.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def log(self, message: str):
        """Logs a message to the file."""
        timestamp = datetime.datetime.now().isoformat()
        with open(self.file_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

def main():
    import os
    os.makedirs("logs", exist_ok=True)
    logger = Logger("logs/app.log")
    logger.log("Logger initialized")

if __name__ == "__main__":
    main()
