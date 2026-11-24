import unittest

from src.hash_table import HashTable, horner_steps
from src.linear_probing import LinearProbingHashTable


class TestHornerHash(unittest.TestCase):
    def test_empty_string_hashes_to_zero(self):
        self.assertEqual(horner_steps("", 11), [])

    def test_horner_steps_are_in_bucket_range(self):
        steps = horner_steps("URL", 11)

        self.assertEqual(len(steps), 3)
        for _, _, _, result in steps:
            self.assertGreaterEqual(result, 0)
            self.assertLess(result, 11)

    def test_anagrams_are_distributed_across_buckets(self):
        anagrams = ["stop", "pots", "tops", "spot", "opts", "post"]
        bucket_indexes = []

        for key in anagrams:
            steps = horner_steps(key, 11)
            bucket_index = steps[-1][3]
            if bucket_index not in bucket_indexes:
                bucket_indexes.append(bucket_index)

        self.assertGreater(len(bucket_indexes), 1)


class TestHashTable(unittest.TestCase):
    def test_put_get_delete_and_missing_key(self):
        table = HashTable(capacity=11)

        table.put("name", "copilot")
        self.assertEqual(table.get("name"), "copilot")
        self.assertTrue("name" in table)

        table.delete("name")
        self.assertIsNone(table.get("name"))
        self.assertFalse("name" in table)

    def test_overwriting_existing_key_keeps_size(self):
        table = HashTable(capacity=11)

        table.put("key", "old")
        table.put("key", "new")

        self.assertEqual(len(table), 1)
        self.assertEqual(table.get("key"), "new")

    def test_delete_missing_key_is_safe(self):
        table = HashTable(capacity=11)

        table.delete("missing")

        self.assertEqual(len(table), 0)
        self.assertIsNone(table.get("missing"))

    def test_collision_nodes_are_searched(self):
        table = HashTable(capacity=3)
        table.put("a", 1)
        table.put("d", 4)

        self.assertEqual(table.get("d"), 4)
        self.assertEqual(table.last_probes, 2)

    def test_rehash_preserves_all_entries(self):
        table = HashTable(capacity=4, max_load=0.75)

        for number in range(4):
            table.put(str(number), number)

        for number in range(4):
            self.assertEqual(table.get(str(number)), number)
        self.assertGreater(table.capacity, 4)

    def test_fixed_capacity_does_not_rehash(self):
        table = HashTable(capacity=4, max_load=None)

        for number in range(20):
            table.put(str(number), number)

        self.assertEqual(table.capacity, 4)
        for number in range(20):
            self.assertEqual(table.get(str(number)), number)

    def test_empty_bucket_probe_count_is_zero(self):
        table = HashTable(capacity=11)

        self.assertIsNone(table.get("missing"))
        self.assertEqual(table.last_probes, 0)


class TestLinearProbingHashTable(unittest.TestCase):
    def test_put_get_delete_and_missing_key(self):
        table = LinearProbingHashTable(capacity=11)

        table.put("name", "copilot")
        self.assertEqual(table.get("name"), "copilot")

        table.delete("name")
        self.assertIsNone(table.get("name"))
        self.assertFalse("name" in table)

    def test_overwriting_existing_key_keeps_size(self):
        table = LinearProbingHashTable(capacity=11)

        table.put("key", "old")
        table.put("key", "new")

        self.assertEqual(len(table), 1)
        self.assertEqual(table.get("key"), "new")

    def test_probe_wraps_from_last_slot_to_first_slot(self):
        table = LinearProbingHashTable(capacity=11, max_load=None)
        first = "b"
        second = None

        for suffix in range(1, 1000):
            candidate = "b" + str(suffix)
            if horner_steps(candidate, 11)[-1][3] == horner_steps(first, 11)[-1][3]:
                second = candidate
                break

        self.assertIsNotNone(second)
        table.put(first, "first")
        table.put(second, "second")

        self.assertEqual(table.get(second), "second")

    def test_delete_with_tombstone_preserves_later_key(self):
        table = LinearProbingHashTable(capacity=11, max_load=None)
        first = "b"
        second = None

        for suffix in range(1, 1000):
            candidate = "b" + str(suffix)
            if horner_steps(candidate, 11)[-1][3] == horner_steps(first, 11)[-1][3]:
                second = candidate
                break

        table.put(first, "first")
        table.put(second, "second")
        table.delete(first)

        self.assertIsNone(table.get(first))
        self.assertEqual(table.get(second), "second")

    def test_fixed_full_table_rejects_new_key(self):
        table = LinearProbingHashTable(capacity=3, max_load=None)
        table.put("a", 1)
        table.put("b", 2)
        table.put("c", 3)

        with self.assertRaises(OverflowError):
            table.put("d", 4)

    def test_missing_key_in_full_table_ends_without_loop(self):
        table = LinearProbingHashTable(capacity=3, max_load=None)
        table.put("a", 1)
        table.put("b", 2)
        table.put("c", 3)

        self.assertIsNone(table.get("missing"))
        self.assertEqual(table.last_probes, 3)


if __name__ == "__main__":
    unittest.main()
