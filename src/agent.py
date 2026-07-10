import datetime

class Task:
    def __init__(self, task_id: int, description: str):
        self.id = task_id
        self.description = description
        self.completed = False

    def __repr__(self):
        return f"Task(id={self.id}, description='{self.description}', completed={self.completed})"

class AgentState:
    """
    Represents the current state of an autonomous agent.
    """
    def __init__(self, name: str):
        self.name = name
        self.goals = []
        self.capabilities = []
        self.tasks = []
        self.plugins = []
        self.is_active = True
        self.logger = None

    def set_logger(self, logger):
        """Sets the logger for the agent."""
        self.logger = logger

    def _log(self, message: str):
        """Logs a message if a logger is set."""
        if self.logger:
            self.logger.log(message)

    def add_goal(self, goal: str):
        """Adds a new goal to the agent's goals list."""
        if goal not in self.goals:
            self.goals.append(goal)
            self._log(f"Added goal: {goal}")

    def add_capability(self, capability: str):
        """Adds a new capability to the agent's capabilities list."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self._log(f"Added capability: {capability}")

    def add_task(self, task_id: int, description: str):
        """Adds a new task to the agent's tasks list."""
        self.tasks.append(Task(task_id, description))
        self._log(f"Added task: {description}")

    def complete_task(self, task_id: int):
        """Marks a task as completed by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                self._log(f"Completed task: {task.description}")
                return True
        return False

    def add_plugin(self, plugin):
        """Installs and initializes a plugin."""
        plugin.setup(self)
        self.plugins.append(plugin)
        self._log(f"Added plugin: {plugin.name}")

    def get_plugin(self, plugin_name: str):
        """Retrieves a plugin by its name."""
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                return plugin
        return None

    def run_plugin(self, plugin_name: str):
        """Runs a plugin by its name."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.execute(self)
            self._log(f"Executed plugin: {plugin.name}")
            return True
        return False

    def get_summary(self) -> str:
        """Returns a summary string of the agent's current state."""
        return f"Agent: {self.name} | Goals: {len(self.goals)} | Capabilities: {len(self.capabilities)} | Tasks: {len(self.tasks)} | Plugins: {len(self.plugins)}"
