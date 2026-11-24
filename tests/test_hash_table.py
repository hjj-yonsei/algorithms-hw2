import unittest
from src.hash_table import HashTable, compute_horner


class TestHornerHash(unittest.TestCase):
    def test_empty_string_and_known_values(self):
        self.assertEqual(compute_horner("", 97), 0)
        self.assertEqual(compute_horner("a", 97), 0)
        self.assertEqual(compute_horner("ab", 97), 1)

    def test_anagrams_spread(self):
        words = ["stop", "pots", "tops", "spot", "opts", "post"]
        indices = {compute_horner(w, 97) for w in words}
        self.assertGreaterEqual(len(indices), 5)


class TestChainingHashTable(unittest.TestCase):
    def test_put_get_update_delete(self):
        ht = HashTable(capacity=11, max_load=0.75)
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
        ht = HashTable(capacity=5, max_load=0.7)
        for i in range(30):
            ht.put(f"https://example.com/{i}", str(i))
        self.assertEqual(len(ht), 30)
        self.assertGreater(ht.capacity, 5)
        for i in range(30):
            self.assertEqual(ht.get(f"https://example.com/{i}"), str(i))

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


if __name__ == "__main__":
    unittest.main()
