"""装备预设：保存当前装备、整体套用预设、对比变化、汇总属性。

apply 先整体校验再整体换装，要么完全成功要么完全不动；
stats() 从当前 equipped 现算；查物品走 id 索引，不按名字扫库。
"""


class Armory:
    """装备与预设。"""

    def __init__(self, catalog, player_level=1):
        self.catalog = catalog
        self.player_level = player_level
        self.equipped = {}
        self.presets = {}
        self.scanned = 0
        self.last_invalid = []
        self._by_id = {}
        for item in catalog:
            self._by_id.setdefault(item["id"], item)

    def _find(self, item_id):
        self.scanned += 1
        return self._by_id.get(item_id)

    def save_preset(self, name):
        """把当前装备存成预设。"""
        self.presets[name] = dict(self.equipped)
        return dict(self.equipped)

    def apply(self, name):
        """整体套用预设：全部条目合格才换装，否则 equipped 不动。"""
        preset = self.presets[name]
        invalid = []
        for slot, item_id in preset.items():
            item = self._find(item_id)
            if (item is None or item["slot"] != slot
                    or item["min_level"] > self.player_level):
                invalid.append(slot)
        self.last_invalid = sorted(invalid)
        if invalid:
            return False
        self.equipped = dict(preset)
        return True

    def stats(self):
        """从当前 equipped 现算属性汇总，同属性相加。"""
        total = {}
        for item_id in self.equipped.values():
            item = self._by_id.get(item_id)
            if item is None:
                continue
            for stat, value in item["stats"].items():
                total[stat] = total.get(stat, 0) + value
        return total

    def diff(self, name):
        """相对当前装备的变化：added / removed / changed，均按槽位名排序。"""
        preset = self.presets[name]
        added = [slot for slot in preset if slot not in self.equipped]
        removed = [slot for slot in self.equipped if slot not in preset]
        changed = [slot for slot in preset
                   if slot in self.equipped and self.equipped[slot] != preset[slot]]
        return sorted(added), sorted(removed), sorted(changed)
