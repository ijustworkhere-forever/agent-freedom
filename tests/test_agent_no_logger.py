import unittest
from src.agent import AgentState
from src.logger import Logger

class MockPlugin:
    def __init__(self):
        self.name = "MockPlugin"
    def setup(self, agent): pass
    def execute(self, agent): return True

class TestAgentNoLogger(unittest.TestCase):
    def setUp(self):
        self.agent = AgentState("NoLoggerAgent")

    def test_no_logger_behavior(self):
        # Test that adding goals/capabilities/tasks/plugins doesn't fail without a logger
        self.agent.add_goal("No logger goal")
        self.agent.add_capability("No logger capability")
        self.agent.add_task(1, "No logger task")
        self.agent.add_plugin(MockPlugin())

        self.assertEqual(self.agent.goals, ["No logger goal"])
        self.assertEqual(self.agent.capabilities, ["No logger capability"])
        self.assertEqual(len(self.agent.tasks), 1)
        self.assertEqual(len(self.agent.plugins), 1)

if __name__ == "__main__":
    unittest.main()
