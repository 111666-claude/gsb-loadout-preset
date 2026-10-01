import unittest

from loadout.core import Armory


def catalog():
    return [
        {"id": "sword", "slot": "weapon", "min_level": 1, "stats": {"power": 100}},
        {"id": "shield", "slot": "offhand", "min_level": 1, "stats": {"armor": 40}},
    ]


class BasicTest(unittest.TestCase):
    def test_empty_stats(self):
        self.assertEqual(Armory(catalog()).stats(), {})

    def test_unknown_preset_raises(self):
        with self.assertRaises(KeyError):
            Armory(catalog()).apply("nope")

    def test_valid_preset_equips_items(self):
        armory = Armory(catalog())
        armory.presets["p"] = {"weapon": "sword"}
        self.assertTrue(armory.apply("p"))
        self.assertEqual(armory.equipped["weapon"], "sword")

    def test_save_preset_snapshots_current_equipment(self):
        armory = Armory(catalog())
        armory.equipped["weapon"] = "sword"
        saved = armory.save_preset("p")
        self.assertEqual(saved, {"weapon": "sword"})
        armory.equipped.clear()
        self.assertEqual(armory.presets["p"], {"weapon": "sword"})


class DiffTest(unittest.TestCase):
    def test_no_change_is_empty(self):
        armory = Armory(catalog())
        armory.equipped["weapon"] = "sword"
        armory.save_preset("p")
        added, removed, changed = armory.diff("p")
        self.assertEqual((added, removed, changed), ([], [], []))


if __name__ == "__main__":
    unittest.main()
