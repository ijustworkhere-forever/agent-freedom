import subprocess
import time
import psutil
from abc import ABC, abstractmethod

class Plugin(ABC):
    """
    Abstract base class for all agent plugins.
    """
    def __init__(self, command: str = None):
        self.name = self.__class__.__name__
        self.command = command

    def setup(self, agent):
        """Initialize the plugin with the given agent."""
        pass

    @abstractmethod
    def execute(self, agent):
        """Execute the plugin's primary functionality."""
        pass

class TestPlugin(Plugin):
    """
    A plugin that executes a shell command and returns the result.
    """
    def __init__(self, command: str):
        super().__init__(command)
        self.last_result = None

    def execute(self, agent):
        result = subprocess.run(self.command, shell=True, capture_output=True, text=True)
        self.last_result = {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        return self.last_result

class BenchmarkPlugin(Plugin):
    """
    A plugin that benchmarks the execution time of a shell command.
    """
    def __init__(self, command: str, iterations: int = 1):
        super().__init__(command)
        self.iterations = iterations
        self.results = []

    def execute(self, agent):
        import statistics
        times = []
        failures = 0

        for _ in range(self.iterations):
            try:
                start_time = time.time()
                result = subprocess.run(self.command, shell=True, capture_output=True, text=True)
                end_time = time.time()

                if result.returncode == 0:
                    times.append(end_time - start_time)
                else:
                    failures += 1
            except Exception:
                failures += 1

        if not times:
            summary = {
                "command": self.command,
                "success_count": 0,
                "failure_count": failures,
                "statistics": None
            }
        else:
            summary = {
                "command": self.command,
                "success_count": len(times),
                "failure_count": failures,
                "statistics": {
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "min": min(times),
                    "max": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0.0
                }
            }

        self.results.append(summary)
        return summary

class ResourceMonitoringPlugin(Plugin):
    """
    A plugin that monitors CPU and memory usage while running a command.
    """
    def __init__(self, command: str):
        super().__init__(command)
        self.results = []

    def execute(self, agent):
        process = subprocess.Popen(self.command, shell=True)
        cpu_usages = []
        mem_usages = []

        while process.poll() is None:
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                mem = psutil.Process(process.pid).memory_info().rss / (1024 * 1024) # MB
                cpu_usages.append(cpu)
                mem_usages.append(mem)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

        process.wait()

        max_cpu = max(cpu_usages) if cpu_usages else 0
        max_mem = max(mem_usages) if mem_usages else 0

        result = {
            "command": self.command,
            "max_cpu_percent": max_cpu,
            "max_mem_mb": max_mem,
            "success": process.returncode == 0
        }
        self.results.append(result)
        return result

import os
from pathlib import Path

class MemoryPlugin(Plugin):
    """
    A plugin that manages persistent knowledge in the repository's memory directory.
    """
    def __init__(self, base_dir: str = "memory"):
        super().__init__()
        self.base_dir = Path(base_dir)
        self._ensure_dirs()

    def _ensure_dirs(self):
        for category in ["lessons", "failures", "discoveries"]:
            (self.base_dir / category).mkdir(parents=True, exist_ok=True)

    def execute(self, agent):
        # The default execute does nothing
        pass

    def add_knowledge(self, category: str, title: str, content: str):
        category_path = self.base_dir / category
        if not category_path.exists():
            category_path.mkdir(parents=True, exist_ok=True)

        file_path = category_path / f"{title.lower().replace(' ', '_')}.md"
        with open(file_path, "w") as f:
            f.write(f"# {title}\n\n{content}")

    def append_to_index(self, content: str):
        index_path = self.base_dir / "MEMORY.md"
        with open(index_path, "a") as f:
            f.write(f"\n{content}\n")

    def get_knowledge(self, category: str):
        category_path = self.base_dir / category
        if not category_path.exists():
            return []
        return [f.stem for f in category_path.glob("*.md")]
