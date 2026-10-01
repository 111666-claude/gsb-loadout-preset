"""装备预设：保存当前装备、整体套用预设、对比变化、汇总属性。

缺陷：套用失败时前面已经改掉、属性每次套用都累加、diff 不算被移除的槽、
槽位归属不校验、按物品名线性查找。
"""


class Armory:
    """装备与预设。"""

    def __init__(self, catalog, player_level=1):
        self.catalog = catalog
        self.player_level = player_level
        self.equipped = {}
        self.bonus = {}
        self.presets = {}
        self.scanned = 0

    def _find(self, item_id):
        for item in self.catalog:
            self.scanned += 1
            if item["id"] == item_id:
                return item
        return None

    def save_preset(self, name):
        """把当前装备存成预设。"""
        self.presets[name] = dict(self.equipped)
        return dict(self.equipped)

    def apply(self, name):
        """整体套用预设。"""
        preset = self.presets[name]
        for slot, item_id in preset.items():
            item = self._find(item_id)
            if item is None or item["min_level"] > self.player_level:
                return False
            self.equipped[slot] = item_id
            for stat, value in item["stats"].items():
                self.bonus[stat] = self.bonus.get(stat, 0) + value
        return True

    def stats(self):
        """当前装备的属性汇总。"""
        return dict(self.bonus)

    def diff(self, name):
        """相对当前装备的变化。"""
        preset = self.presets[name]
        added = [slot for slot in preset if slot not in self.equipped]
        removed = []
        changed = [slot for slot in preset
                   if slot in self.equipped and self.equipped[slot] != preset[slot]]
        return sorted(added), sorted(removed), sorted(changed)
