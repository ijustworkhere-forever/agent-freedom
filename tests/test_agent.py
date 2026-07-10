import unittest
import os
import tempfile
import shutil
import unittest.mock
from src.agent import AgentState
from src.logger import Logger
from src.plugins import TestPlugin, BenchmarkPlugin, ResourceMonitoringPlugin, MemoryPlugin

class MockPlugin:
    def __init__(self):
        self.name = "MockPlugin"
    def setup(self, agent): pass
    def execute(self, agent): return True

class TestAgentState(unittest.TestCase):
    def setUp(self):
        self.test_log = "tests/test_agent_logger.log"
        self.logger = Logger(self.test_log)
        self.agent = AgentState("TestAgent")
        self.agent.set_logger(self.logger)

        # Create a temporary directory for plugin tests
        self.test_dir = tempfile.mkdtemp()
        self.memory_plugin = MemoryPlugin(base_dir=self.test_dir)
        self.agent.add_plugin(self.memory_plugin)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_agent_state_initialization(self: unittest.TestCase):
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.goals, [])
        self.assertEqual(self.agent.capabilities, [])
        self.assertEqual(self.agent.tasks, [])
        self.assertEqual(len(self.agent.plugins), 1) # Added MemoryPlugin in setUp
        self.assertTrue(self.agent.is_active)

    def test_agent_add_goal(self: unittest.TestCase):
        self.agent.add_goal("Improve testing")
        self.assertIn("Improve testing", self.agent.goals)
        self.assertEqual(len(self.agent.goals), 1)
        with open(self.test_log, "r") as f:
            content = f.read()
        self.assertIn("Added goal: Improve testing", content)

    def test_agent_add_goal_duplicate(self: unittest.TestCase):
        self.agent.add_goal("Improve testing")
        self.agent.add_goal("Improve testing")
        self.assertEqual(len(self.agent.goals), 1)

    def test_agent_add_capability(self: unittest.TestCase):
        self.agent.add_capability("Running tests")
        self.assertIn("Running tests", self.agent.capabilities)
        self.assertEqual(len(self.agent.goals), 0)
        self.assertEqual(len(self.agent.capabilities), 1)
        with open(self.test_log, "r") as f:
            content = f.read()
        self.assertIn("Added capability: Running tests", content)

    def test_agent_add_capability_duplicate(self: unittest.TestCase):
        self.agent.add_capability("Running tests")
        self.agent.add_capability("Running tests")
        self.assertEqual(len(self.agent.capabilities), 1)

    def test_agent_task_management(self: unittest.TestCase):
        self.agent.add_task(1, "First task")
        self.assertEqual(len(self.agent.tasks), 1)
        self.assertEqual(self.agent.tasks[0].description, "First task")
        self.assertFalse(self.agent.tasks[0].completed)

        self.agent.complete_task(1)
        self.assertTrue(self.agent.tasks[0].completed)
        with open(self.test_log, "r") as f:
            content = f.read()
        self.assertIn("Completed task: First task", content)

    def test_agent_complete_task_invalid_id(self: unittest.TestCase):
        self.agent.add_task(1, "First task")
        result = self.agent.complete_task(999)
        self.assertFalse(result)

    def test_agent_complete_task_already_completed(self: unittest.TestCase):
        self.agent.add_task(1, "First task")
        self.agent.complete_task(1)
        result = self.agent.complete_task(1)
        self.assertTrue(result)

    def test_agent_plugin_management(self: unittest.TestCase):
        plugin = MockPlugin()
        self.agent.add_plugin(plugin)
        self.assertIn("Plugins: 2", self.agent.get_summary()) # MemoryPlugin + MockPlugin

        success = self.agent.run_plugin("MockPlugin")
        self.assertTrue(success)
        with open(self.test_log, "r") as f:
            content = f.read()
        self.assertIn("Executed plugin: MockPlugin", content)

    def test_agent_run_plugin_invalid_name(self: unittest.TestCase):
        result = self.agent.run_plugin("NonExistentPlugin")
        self.assertFalse(result)

    def test_test_plugin_execution(self: unittest.TestCase):
        # Test the actual TestPlugin with a command that succeeds
        tp = TestPlugin("echo hello_world")
        self.agent.add_plugin(tp)
        success = self.agent.run_plugin("TestPlugin")
        self.assertTrue(success)
        self.assertTrue(tp.last_result["success"])
        self.assertEqual(tp.last_result["stdout"].strip(), "hello_world")

    def test_benchmark_plugin_with_failures(self: unittest.TestCase):
        # 'exit 1' will cause failures.
        # We use a command that is guaranteed to fail.
        bp = BenchmarkPlugin("exit 1", iterations=3)
        self.agent.add_plugin(bp)
        success = self.agent.run_plugin("BenchmarkPlugin")
        self.assertTrue(success)
        self.assertEqual(bp.results[0]["success_count"], 0)
        self.assertEqual(bp.results[0]["failure_count"], 3)
        self.assertIsNone(bp.results[0]["statistics"])

    def test_benchmark_plugin_mixed_results(self: unittest.TestCase):
        # Using a stateful command to trigger the 'else' block (line 75)
        # The command will succeed on the first attempt and fail on subsequent ones.
        state_file = os.path.abspath(os.path.join(self.test_dir, "state.txt")).replace('\\', '/')
        with open(state_file, "w") as f:
            f.write("") # Start with empty file

        # Command: if state is empty then exit 0 else exit 1
        cmd = f"python -c \"import os, sys; f=open('{state_file}', 'r'); c=f.read(); f.close(); sys.exit(0 if c=='' else 1)\" && echo 1 >> '{state_file}'"

        print(f"DEBUG: command: {cmd}")

        bp = BenchmarkPlugin(cmd, iterations=2)
        self.agent.add_plugin(bp)
        success = self.agent.run_plugin("BenchmarkPlugin")
        self.assertTrue(success)
        print(f"DEBUG: results: {bp.results[0]}")
        self.assertEqual(bp.results[0]["success_count"], 1)
        self.assertEqual(bp.results[0]["failure_count"], 1)
        self.assertIsNotNone(bp.results[0]["statistics"])

    @unittest.mock.patch('subprocess.run')
    def test_benchmark_plugin_exception(self, mock_run):
        mock_run.side_effect = Exception("Mocked exception")
        bp = BenchmarkPlugin("echo hello", iterations=1)
        self.agent.add_plugin(bp)
        success = self.agent.run_plugin("BenchmarkPlugin")
        self.assertTrue(success)
        self.assertEqual(bp.results[0]["failure_count"], 1)

    def test_resource_monitoring_plugin_execution(self: unittest.TestCase):
        rmp = ResourceMonitoringPlugin("echo 'resource monitoring test' && sleep 1")
        self.agent.add_plugin(rmp)
        success = self.agent.run_plugin("ResourceMonitoringPlugin")
        self.assertTrue(success)
        self.assertIn("max_cpu_percent", rmp.results[0])
        self.assertIn("max_mem_mb", rmp.results[0])
        self.assertTrue(rmp.results[0]["success"])

    def test_resource_monitoring_plugin_failure(self: unittest.TestCase):
        rmp = ResourceMonitoringPlugin("exit 1")
        self.agent.add_plugin(rmp)
        success = self.agent.run_plugin("ResourceMonitoringPlugin")
        self.assertTrue(success)
        self.assertFalse(rmp.results[0]["success"])

    def test_agent_summary(self: unittest.TestCase):
        self.agent.add_goal("Goal 1")
        self.agent.add_capability("Cap 1")
        self.agent.add_task(1, "Task 1")
        self.agent.add_plugin(TestPlugin("echo"))
        summary = self.agent.get_summary()
        self.assertIn("Agent: TestAgent", summary)
        self.assertIn("Goals: 1", summary)
        self.assertIn("Capabilities: 1", summary)
        self.assertIn("Tasks: 1", summary)
        self.assertIn("Plugins: 2", summary) # MemoryPlugin + TestPlugin

    def test_task_repr(self: unittest.TestCase):
        from src.agent import Task
        task = Task(1, "Test task")
        self.assertEqual(repr(task), "Task(id=1, description='Test task', completed=False)")

    def test_memory_plugin_add_knowledge(self: unittest.TestCase):
        mp = self.memory_plugin
        mp.add_knowledge("lessons", "Test Lesson", "This is a test lesson content.")
        self.assertIn("test_lesson", mp.get_knowledge("lessons"))

    def test_memory_plugin_edge_cases(self: unittest.TestCase):
        mp = self.memory_plugin
        # Test get_knowledge with non-existent category
        self.assertEqual(mp.get_knowledge("non_existent_category"), [])

        # Test add_knowledge with existing directory (should not fail)
        mp.add_knowledge("lessons", "Existing Lesson", "Content")
        self.assertIn("existing_lesson", mp.get_knowledge("lessons"))

    def test_memory_plugin_append_to_index(self: unittest.TestCase):
        mp = self.memory_plugin
        mp.append_to_index("New entry in index")
        index_path = os.path.join(self.test_dir, "MEMORY.md")
        with open(index_path, "r") as f:
            content = f.read()
        self.assertIn("New entry in index", content)

if __name__ == '__main__':
    unittest.main()
