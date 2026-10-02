"""装备预设：保存当前装备、整体套用预设、对比变化、汇总属性。"""


class Armory:
    """装备与预设。"""

    def __init__(self, catalog, player_level=1):
        self.catalog = catalog
        self.player_level = player_level
        self.equipped = {}
        self.presets = {}
        self.scanned = 0
        self.invalid_slots = []
        self._items = {item["id"]: item for item in catalog}

    def _get(self, item_id):
        """按 id O(1) 取物品；每次查询计一次 scanned。"""
        self.scanned += 1
        return self._items.get(item_id)

    def save_preset(self, name):
        """把当前装备存成预设。"""
        self.presets[name] = dict(self.equipped)
        return dict(self.equipped)

    def apply(self, name):
        """整体套用预设：全部合格才提交，否则 equipped 完全不动。"""
        preset = self.presets[name]
        resolved = {}
        invalid = []
        for slot, item_id in preset.items():
            item = self._get(item_id)
            if (item is None
                    or item.get("slot") != slot
                    or item.get("min_level", 0) > self.player_level):
                invalid.append(slot)
            else:
                resolved[slot] = (item_id, item)
        if invalid:
            self.invalid_slots = sorted(invalid)
            return False
        self.invalid_slots = []
        self.equipped = {slot: item_id for slot, (item_id, _item) in resolved.items()}
        return True

    def stats(self):
        """从当前 equipped 现算属性，同一属性相加。"""
        total = {}
        for item_id in self.equipped.values():
            item = self._items.get(item_id)
            if item is None:
                continue
            for stat, value in item.get("stats", {}).items():
                total[stat] = total.get(stat, 0) + value
        return total

    def diff(self, name):
        """相对当前装备的变化：added/removed/changed，均按槽位名排序。"""
        preset = self.presets[name]
        added = [slot for slot in preset if slot not in self.equipped]
        removed = [slot for slot in self.equipped if slot not in preset]
        changed = [slot for slot in preset
                   if slot in self.equipped and self.equipped[slot] != preset[slot]]
        return sorted(added), sorted(removed), sorted(changed)
