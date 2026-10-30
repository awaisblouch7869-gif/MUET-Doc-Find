import unittest

from src.hash_table import HashTable, default_hash, always_zero


class TestDefaultHash(unittest.TestCase):
    def test_known_values_are_the_same_on_every_run(self):
        self.assertEqual(default_hash(""), 5381)
        self.assertEqual(default_hash("a"), 177670)

    def test_same_key_gives_same_number(self):
        self.assertEqual(default_hash("hash"), default_hash("hash"))

    def test_different_keys_usually_give_different_numbers(self):
        self.assertNotEqual(default_hash("data"), default_hash("structures"))


class TestBasicOperations(unittest.TestCase):
    def test_new_table_is_empty(self):
        table = HashTable()
        self.assertEqual(len(table), 0)
        self.assertEqual(table.keys(), [])
        self.assertFalse(table.contains("data"))
        self.assertIsNone(table.get("data"))

    def test_put_then_get(self):
        table = HashTable()
        self.assertTrue(table.put("data", 1))
        self.assertEqual(table.get("data"), 1)
        self.assertTrue(table.contains("data"))
        self.assertEqual(len(table), 1)

    def test_put_on_existing_key_updates_value(self):
        table = HashTable()
        table.put("data", 1)
        self.assertFalse(table.put("data", 2))
        self.assertEqual(table.get("data"), 2)
        self.assertEqual(len(table), 1)

    def test_get_missing_key_returns_default(self):
        table = HashTable()
        self.assertEqual(table.get("nothing", 0), 0)

    def test_keys_are_case_sensitive(self):
        table = HashTable()
        table.put("Data", 1)
        self.assertFalse(table.contains("data"))

    def test_empty_string_is_a_valid_key(self):
        table = HashTable()
        table.put("", 7)
        self.assertEqual(table.get(""), 7)

    def test_remove(self):
        table = HashTable()
        table.put("data", 1)
        self.assertTrue(table.remove("data"))
        self.assertFalse(table.contains("data"))
        self.assertEqual(len(table), 0)
        self.assertFalse(table.remove("data"))

    def test_non_string_key_is_rejected(self):
        table = HashTable()
        with self.assertRaises(TypeError):
            table.put(5, "x")
        with self.assertRaises(TypeError):
            table.get(None)

    def test_bad_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            HashTable(initial_size=0)
        with self.assertRaises(ValueError):
            HashTable(max_load_factor=0)


class TestResizing(unittest.TestCase):
    def test_table_grows_and_keeps_every_entry(self):
        table = HashTable()
        for number in range(200):
            table.put("word" + str(number), number)
        self.assertEqual(len(table), 200)
        self.assertGreater(table.bucket_count(), 8)
        for number in range(200):
            self.assertEqual(table.get("word" + str(number)), number)

    def test_load_factor_stays_within_the_limit(self):
        table = HashTable()
        for number in range(200):
            table.put("word" + str(number), number)
        self.assertLessEqual(table.load_factor(), 0.75)

    def test_same_insertions_give_same_layout(self):
        first = HashTable()
        second = HashTable()
        for number in range(50):
            first.put("w" + str(number), number)
            second.put("w" + str(number), number)
        self.assertEqual(first.keys(), second.keys())


class TestCollisions(unittest.TestCase):
    def test_forced_collisions_with_terrible_hash(self):
        table = HashTable(initial_size=8, hash_function=always_zero)
        for key in ["a", "b", "c"]:
            table.put(key, key.upper())
        self.assertEqual(table.bucket_keys(0), ["c", "b", "a"])  # newest first
        self.assertEqual(table.longest_chain(), 3)
        self.assertEqual(table.collision_count(), 2)
        self.assertEqual(table.get("a"), "A")
        self.assertEqual(table.get("b"), "B")
        self.assertEqual(table.get("c"), "C")

    def test_collisions_with_our_real_hash_when_table_has_one_bucket(self):
        table = HashTable(initial_size=1, max_load_factor=1000)
        for key in ["data", "lab", "exam"]:
            table.put(key, len(key))
        self.assertEqual(table.bucket_count(), 1)
        self.assertEqual(table.longest_chain(), 3)
        self.assertEqual(table.get("lab"), 3)

    def test_update_inside_a_collision_chain(self):
        table = HashTable(hash_function=always_zero)
        table.put("a", 1)
        table.put("b", 2)
        table.put("a", 99)
        self.assertEqual(table.get("a"), 99)
        self.assertEqual(table.get("b"), 2)
        self.assertEqual(len(table), 2)

    def test_remove_middle_front_and_last_of_a_chain(self):
        table = HashTable(hash_function=always_zero)
        for key in ["a", "b", "c"]:
            table.put(key, 1)
        self.assertEqual(table.bucket_keys(0), ["c", "b", "a"])
        table.remove("b")                                  # middle
        self.assertEqual(table.bucket_keys(0), ["c", "a"])
        table.remove("c")                                  # front
        self.assertEqual(table.bucket_keys(0), ["a"])
        table.remove("a")                                  # last one left
        self.assertEqual(table.bucket_keys(0), [])
        self.assertEqual(len(table), 0)

    def test_everything_survives_a_resize_when_all_keys_collide(self):
        table = HashTable(initial_size=2, hash_function=always_zero)
        for number in range(20):
            table.put("k" + str(number), number)
        self.assertGreater(table.bucket_count(), 2)
        for number in range(20):
            self.assertEqual(table.get("k" + str(number)), number)


if __name__ == "__main__":
    unittest.main()