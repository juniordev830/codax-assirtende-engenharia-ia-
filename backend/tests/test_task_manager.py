import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import task_manager


class TaskManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.patch_dir = patch.object(task_manager, "DATA_DIR", Path(self.temp.name))
        self.patch_db = patch.object(task_manager, "DB_PATH", Path(self.temp.name) / "test.sqlite3")
        self.patch_dir.start()
        self.patch_db.start()
        self.addCleanup(self.patch_dir.stop)
        self.addCleanup(self.patch_db.stop)
        task_manager.initialize_storage()

    def test_task_persists_and_updates(self):
        task = task_manager.create_task("  Corrigir testes ", "Descrição")
        self.assertEqual(task["state"], "planned")
        updated = task_manager.update_task(
            task["id"], state="running", progress=25,
            steps=[{"title": "Analisar", "state": "done"}],
        )
        self.assertEqual(updated["progress"], 25)
        self.assertEqual(task_manager.get_task(task["id"])["steps"][0]["state"], "done")

    def test_invalid_state_is_rejected(self):
        task = task_manager.create_task("Tarefa", "Descrição")
        with self.assertRaises(ValueError):
            task_manager.update_task(task["id"], state="magic")

    def test_usage_cost_is_recorded(self):
        cost = task_manager.record_api_usage("test-model", 1_000_000, 100_000, 1.0, 2.0)
        self.assertAlmostEqual(cost, 1.2)
        self.assertAlmostEqual(task_manager.month_spend_usd(), 1.2)


if __name__ == "__main__":
    unittest.main()
