import unittest
from src.agent import AgentState
from src.logger import Logger
from src.plugins import TestPlugin, BenchmarkPlugin, ResourceMonitoringPlugin
import os

class TestAgentIntegration(unittest.TestCase):
    def setUp(self):
        self.test_log = "tests/test_integration.log"
        self.logger = Logger(self.test_log)
        self.agent = AgentState("IntegrationAgent")
        self.agent.set_logger(self.logger)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def test_full_agent_lifecycle(self):
        # 1. Add goal
        goal = "Test goal"
        self.agent.add_goal(goal)
        self.assertIn(goal, self.agent.goals)

        # 2. Add capability
        cap = "Test capability"
        self.agent.add_capability(cap)
        self.assertIn(cap, self.agent.capabilities)

        # 3. Add task
        task_id = 100
        task_desc = "Test task"
        self.agent.add_task(task_id, task_desc)
        self.assertEqual(len(self.agent.tasks), 1)
        self.assertEqual(self.agent.tasks[0].description, task_desc)
        self.assertFalse(self.agent.tasks[0].completed)

        # 4. Add and run a plugin
        plugin = TestPlugin("echo integration_test_success")
        self.agent.add_plugin(plugin)
        success = self.agent.run_plugin("TestPlugin")

        self.assertTrue(success)
        self.assertTrue(plugin.last_result["success"])
        self.assertIn("integration_test_success", plugin.last_result["stdout"])

        # 5. Complete task
        self.agent.complete_task(task_id)
        self.assertTrue(self.agent.tasks[0].completed)

        # 6. Verify summary
        summary = self.agent.get_summary()
        self.assertIn("Agent: IntegrationAgent", summary)
        self.assertIn("Goals: 1", summary)
        self.assertIn("Capabilities: 1", summary)
        self.assertIn("Tasks: 1", summary)
        self.assertIn("Plugins: 1", summary)

        # 7. Verify logs
        with open(self.test_log, "r") as f:
            content = f.read()
            self.assertIn("Added goal: Test goal", content)
            self.assertIn("Added capability: Test capability", content)
            self.assertIn("Added task: Test task", content)
            self.assertIn("Executed plugin: TestPlugin", content)
            self.assertIn("Completed task: Test task", content)

if __name__ == "__main__":
    unittest.main()
