"""装备预设。"""
import unittest

from loadout.core import Armory


def catalog():
    return [
        {"id": "sword", "slot": "weapon", "min_level": 1, "stats": {"power": 100}},
        {"id": "dagger", "slot": "weapon", "min_level": 1, "stats": {"power": 60}},
        {"id": "shield", "slot": "offhand", "min_level": 5, "stats": {"armor": 40}},
        {"id": "helm", "slot": "head", "min_level": 1, "stats": {"armor": 10}},
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


class AtomicTest(unittest.TestCase):
    def test_over_level_item_blocks_whole_apply(self):
        armory = Armory(catalog(), player_level=1)
        armory.equipped["weapon"] = "sword"
        armory.presets["p"] = {"weapon": "dagger", "offhand": "shield"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {"weapon": "sword"})

    def test_missing_item_blocks_whole_apply(self):
        armory = Armory(catalog(), player_level=10)
        armory.equipped["weapon"] = "sword"
        armory.presets["p"] = {"weapon": "dagger", "head": "ghost"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {"weapon": "sword"})

    def test_invalid_slots_collected_sorted(self):
        armory = Armory(catalog(), player_level=1)
        armory.presets["p"] = {"offhand": "shield", "head": "ghost"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.last_invalid, ["head", "offhand"])

    def test_failure_does_not_partially_equip(self):
        armory = Armory(catalog(), player_level=1)
        armory.presets["p"] = {"head": "helm", "offhand": "shield"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {})


class SlotTest(unittest.TestCase):
    def test_item_in_wrong_slot_is_rejected(self):
        armory = Armory(catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "helm"}
        self.assertFalse(armory.apply("p"))
        self.assertEqual(armory.equipped, {})

    def test_item_in_own_slot_is_accepted(self):
        armory = Armory(catalog(), player_level=10)
        armory.presets["p"] = {"head": "helm"}
        self.assertTrue(armory.apply("p"))
        self.assertEqual(armory.equipped, {"head": "helm"})


class ApplyResultTest(unittest.TestCase):
    def test_slots_missing_from_preset_are_unequipped(self):
        armory = Armory(catalog(), player_level=10)
        armory.equipped = {"weapon": "sword", "head": "helm"}
        armory.presets["p"] = {"weapon": "dagger"}
        self.assertTrue(armory.apply("p"))
        self.assertEqual(armory.equipped, {"weapon": "dagger"})

    def test_empty_preset_unequips_everything(self):
        armory = Armory(catalog(), player_level=10)
        armory.equipped = {"weapon": "sword", "head": "helm"}
        armory.presets["empty"] = {}
        self.assertTrue(armory.apply("empty"))
        self.assertEqual(armory.equipped, {})


class StatsTest(unittest.TestCase):
    def test_same_stat_sums_across_items(self):
        armory = Armory(catalog(), player_level=10)
        armory.presets["p"] = {"head": "helm", "offhand": "shield"}
        armory.apply("p")
        self.assertEqual(armory.stats(), {"armor": 50})

    def test_stats_recomputed_after_unequip(self):
        armory = Armory(catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "sword"}
        armory.presets["empty"] = {}
        armory.apply("p")
        armory.apply("empty")
        self.assertEqual(armory.stats(), {})


class IdempotentTest(unittest.TestCase):
    def test_reapply_does_not_double_stats(self):
        armory = Armory(catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "sword"}
        armory.apply("p")
        armory.apply("p")
        self.assertEqual(armory.stats(), {"power": 100})

    def test_diff_is_empty_after_apply(self):
        armory = Armory(catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "sword", "head": "helm"}
        armory.apply("p")
        self.assertEqual(armory.diff("p"), ([], [], []))
        armory.apply("p")
        self.assertEqual(armory.diff("p"), ([], [], []))


class DiffTest(unittest.TestCase):
    def test_no_change_is_empty(self):
        armory = Armory(catalog())
        armory.equipped["weapon"] = "sword"
        armory.save_preset("p")
        added, removed, changed = armory.diff("p")
        self.assertEqual((added, removed, changed), ([], [], []))

    def test_removed_slot_reported(self):
        armory = Armory(catalog())
        armory.equipped["weapon"] = "sword"
        armory.presets["empty"] = {}
        added, removed, changed = armory.diff("empty")
        self.assertEqual((added, removed, changed), ([], ["weapon"], []))

    def test_added_changed_and_removed_sorted(self):
        armory = Armory(catalog())
        armory.equipped = {"weapon": "sword", "offhand": "shield"}
        armory.presets["p"] = {"weapon": "dagger", "head": "helm"}
        added, removed, changed = armory.diff("p")
        self.assertEqual(added, ["head"])
        self.assertEqual(removed, ["offhand"])
        self.assertEqual(changed, ["weapon"])


class ScanCostTest(unittest.TestCase):
    def test_lookup_cost_independent_of_catalog_size(self):
        big = catalog() + [
            {"id": "filler-%d" % i, "slot": "weapon", "min_level": 1, "stats": {}}
            for i in range(10000)
        ]
        armory = Armory(big, player_level=10)
        armory.presets["p"] = {"weapon": "filler-9999"}
        self.assertTrue(armory.apply("p"))
        self.assertLessEqual(armory.scanned, 1)


if __name__ == "__main__":
    unittest.main()
