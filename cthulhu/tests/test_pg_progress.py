
from django.test import TestCase
from cthulhu.manager.user_request import PgProgress


class TestPgProgress(TestCase):
    def test_single_block(self):
        pg_progress = PgProgress(10, 20, 10)
        self.assertTrue(pg_progress.is_final_block())
        self.assertEqual(pg_progress.goal, 20)

        with self.assertRaises(AssertionError):
            pg_progress.advance_goal()

    def test_multiple_blocks(self):
        pg_progress = PgProgress(10, 30, 10)

        self.assertFalse(pg_progress.is_final_block())
        self.assertEqual(pg_progress.goal, 20)

        self.assertEqual(pg_progress.get_status(), "Waiting for PG creation (0/20), currently creating PGs 10-20")

        pg_progress.set_created_pg_count(20)
        pg_progress.advance_goal()
        self.assertTrue(pg_progress.is_final_block())
        self.assertEqual(pg_progress.goal, 30)

        self.assertEqual(pg_progress.get_status(), "Waiting for PG creation (10/20)")

        with self.assertRaises(AssertionError):
            pg_progress.advance_goal()
