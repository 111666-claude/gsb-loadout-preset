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


def big_catalog():
    return catalog() + [
        {"id": "dagger", "slot": "weapon", "min_level": 1, "stats": {"power": 60}},
        {"id": "helm", "slot": "head", "min_level": 1, "stats": {"armor": 10}},
        {"id": "relic", "slot": "trinket", "min_level": 5, "stats": {"power": 5}},
    ]


class AtomicTest(unittest.TestCase):
    def test_failed_apply_leaves_equipped_untouched(self):
        armory = Armory(big_catalog(), player_level=1)
        armory.equipped["weapon"] = "sword"
        armory.presets["p"] = {"weapon": "dagger", "trinket": "relic"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {"weapon": "sword"})

    def test_missing_item_blocks_whole_apply(self):
        armory = Armory(big_catalog(), player_level=10)
        armory.equipped["weapon"] = "sword"
        armory.presets["p"] = {"weapon": "dagger", "head": "ghost"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {"weapon": "sword"})

    def test_invalid_slots_collected_sorted(self):
        armory = Armory(big_catalog(), player_level=1)
        armory.presets["p"] = {"trinket": "relic", "head": "ghost"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.invalid_slots, ["head", "trinket"])


class IdempotentTest(unittest.TestCase):
    def test_reapply_does_not_double_stats(self):
        armory = Armory(big_catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "sword"}
        armory.apply("p")
        armory.apply("p")
        self.assertEqual(armory.stats(), {"power": 100})

    def test_reapply_diff_is_empty(self):
        armory = Armory(big_catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "sword", "head": "helm"}
        armory.apply("p")
        armory.apply("p")
        self.assertEqual(armory.diff("p"), ([], [], []))


class SlotTest(unittest.TestCase):
    def test_item_in_wrong_slot_rejected(self):
        armory = Armory(big_catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "helm"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {})

    def test_min_level_gate(self):
        armory = Armory(big_catalog(), player_level=4)
        armory.presets["p"] = {"trinket": "relic"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {})


class DiffFullTest(unittest.TestCase):
    def test_added_removed_changed_sorted(self):
        armory = Armory(big_catalog(), player_level=10)
        armory.equipped = {"weapon": "sword", "head": "helm"}
        armory.presets["p"] = {"weapon": "dagger", "trinket": "relic"}
        added, removed, changed = armory.diff("p")
        self.assertEqual(added, ["trinket"])
        self.assertEqual(removed, ["head"])
        self.assertEqual(changed, ["weapon"])

    def test_apply_replaces_slots_not_in_preset(self):
        armory = Armory(big_catalog(), player_level=10)
        armory.equipped = {"weapon": "sword", "head": "helm"}
        armory.presets["p"] = {"weapon": "dagger"}
        self.assertTrue(armory.apply("p"))
        self.assertEqual(armory.equipped, {"weapon": "dagger"})


class ScanCostTest(unittest.TestCase):
    def test_scan_does_not_grow_with_catalog_size(self):
        big = big_catalog() + [
            {"id": "filler-%d" % i, "slot": "weapon", "min_level": 1, "stats": {}}
            for i in range(10000)
        ]
        armory = Armory(big, player_level=10)
        armory.presets["p"] = {"weapon": "filler-9999"}
        for _ in range(100):
            armory.apply("p")
        self.assertLessEqual(armory.scanned, 100)
