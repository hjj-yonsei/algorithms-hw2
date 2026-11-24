import unittest
from src.hash_table import HashTable, compute_horner
from src.linear_probing import LinearProbingHashTable


class TestHornerHash(unittest.TestCase):
    def test_empty_string_and_known_values(self):
        self.assertEqual(compute_horner("", 97), 0)
        self.assertEqual(compute_horner("a", 97), 0)
        self.assertEqual(compute_horner("ab", 97), 1)

    def test_anagrams_spread(self):
        words = ["stop", "pots", "tops", "spot", "opts", "post"]
        indices = {compute_horner(w, 97) for w in words}
        self.assertGreaterEqual(len(indices), 5)


class BaseHashTableContractMixin:
    def make_table(self, capacity=11, max_load=0.75):
        raise NotImplementedError

    def test_put_get_update_delete(self):
        ht = self.make_table()
        ht.put("https://a.com", "1")
        ht.put("https://b.com", "2")
        self.assertEqual(len(ht), 2)
        self.assertEqual(ht.get("https://a.com"), "1")
        self.assertIn("https://b.com", ht)
        self.assertIsNone(ht.get("https://missing.com"))

        ht.put("https://a.com", "99")
        self.assertEqual(len(ht), 2)
        self.assertEqual(ht.get("https://a.com"), "99")

        self.assertTrue(ht.delete("https://a.com"))
        self.assertFalse(ht.delete("https://a.com"))
        self.assertIsNone(ht.get("https://a.com"))
        self.assertEqual(len(ht), 1)

    def test_resize_preserves_all_entries(self):
        ht = self.make_table(capacity=5, max_load=0.7)
        for i in range(30):
            ht.put(f"https://example.com/{i}", str(i))
        self.assertEqual(len(ht), 30)
        self.assertGreater(ht.capacity, 5)
        for i in range(30):
            self.assertEqual(ht.get(f"https://example.com/{i}"), str(i))


class TestChainingHashTable(BaseHashTableContractMixin, unittest.TestCase):
    def make_table(self, capacity=11, max_load=0.75):
        return HashTable(capacity=capacity, max_load=max_load)

    def test_empty_bucket_probe_count_is_zero(self):
        ht = HashTable(capacity=97, max_load=None)
        val, found, probes = ht.get_with_probes("https://unseen.example.com")
        self.assertIsNone(val)
        self.assertFalse(found)
        self.assertEqual(probes, 0)

    def test_fixed_capacity_allows_load_above_one(self):
        ht = HashTable(capacity=5, max_load=None)
        for i in range(20):
            ht.put(f"key-{i}", i)
        self.assertEqual(ht.capacity, 5)
        self.assertEqual(len(ht), 20)
        for i in range(20):
            self.assertEqual(ht.get(f"key-{i}"), i)


class TestLinearProbingHashTable(BaseHashTableContractMixin, unittest.TestCase):
    def make_table(self, capacity=11, max_load=0.75):
        return LinearProbingHashTable(capacity=capacity, max_load=max_load)

    def test_wrap_around_from_last_slot_to_zero(self):
        ht = LinearProbingHashTable(capacity=5, max_load=None)
        last_slot_keys = [f"k{i}" for i in range(200) if compute_horner(f"k{i}", 5) == 4][:3]
        self.assertEqual(len(last_slot_keys), 3)

        for idx, k in enumerate(last_slot_keys):
            ht.put(k, f"val-{idx}")

        self.assertEqual(ht.keys[4], last_slot_keys[0])
        self.assertEqual(ht.keys[0], last_slot_keys[1])
        self.assertEqual(ht.keys[1], last_slot_keys[2])

        for idx, k in enumerate(last_slot_keys):
            self.assertEqual(ht.get(k), f"val-{idx}")

        self.assertTrue(ht.delete(last_slot_keys[1]))
        self.assertIsNone(ht.get(last_slot_keys[1]))
        self.assertEqual(ht.get(last_slot_keys[2]), "val-2")

    def test_full_table_overflow_and_bounded_search(self):
        ht = LinearProbingHashTable(capacity=5, max_load=None)
        for i in range(5):
            ht.put(f"item-{i}", i)
        self.assertEqual(len(ht), 5)

        with self.assertRaises(OverflowError):
            ht.put("item-overflow", 999)

        val, found, probes = ht.get_with_probes("not-in-full-table")
        self.assertIsNone(val)
        self.assertFalse(found)
        self.assertEqual(probes, 5)


if __name__ == "__main__":
    unittest.main()
