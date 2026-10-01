# loadout-preset

装备预设：把当前装备存成快照，之后整体套用、对比变化、汇总属性。
只用 Python 标准库。

```
python3 -m loadout.cli --sample atomic
python3 -m loadout.cli --sample idempotent
python3 -m loadout.cli --sample diff
python3 -m loadout.cli --sample slot
python3 -m loadout.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **预设内容**：预设是 `{槽位: 物品 id}` 的一份快照。
- **整体套用**：套用前先检查预设里的每一条——物品必须存在、物品自身的槽位必须等于
  预设里的槽位、`min_level` 不得超过玩家等级；只要有一条不满足就整体不生效，
  `equipped` 一个字节都不改，返回 False。不合格的槽位按名字排序收集。
- **套用结果**：全部合格时，`equipped` 恰好等于预设内容，预设里没有的槽位一律卸下。
- **属性汇总**：`stats()` 从当前 `equipped` 现算，同一属性相加；同一预设重复套用
  属性不翻倍。
- **对比**：`diff(name)` 相对当前装备给出 added（预设有、当前没有）、
  removed（当前有、预设没有）、changed（同槽位换了物品），三个列表都按槽位名排序。
- **不变量**：`apply` 要么完全成功要么完全不动；重复套用同一预设的 `diff` 为空。
- **查询代价**：查物品不许按名字扫物品库，`scanned` 不随物品库大小线性增长。
- **规模**：10 万件物品、每秒 10 万次套用与对比，单次 O(预设条目数)。

## 输出契约（不改格式）

```
ok=.. weapon=..
power=..
removed=.. equipped=..
scanned=..
```

## 目录

```
loadout/core.py   预设、套用、对比与属性
loadout/cli.py    命令行入口
tests/            unittest 用例
```
