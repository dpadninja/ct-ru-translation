"""English -> Russian term dictionaries built from already translated list files."""
import loc
from monster_names import NAMES


def pairs(en_name: str, ru_name: str | None = None) -> dict[str, str]:
    en = loc.read(loc.ORIG / "en" / "msg" / en_name)
    ru = loc.read(loc.OUT / (ru_name or en_name))
    out = {}
    for a, b in zip(en, ru):
        ka, kb = loc.key(a), loc.key(b)
        ta = a.split(",", 1)[1] if ka else a
        tb = b.split(",", 1)[1] if kb else b
        if ta.strip() and ta != "Dummy" and ta not in out:
            out[ta] = tb
    return out


def items() -> dict[str, str]:
    return pairs("item.txt")


def techs() -> dict[str, str]:
    return {k.lstrip("★"): v.lstrip("★") for k, v in pairs("tech.txt").items()}


def places() -> dict[str, str]:
    d = pairs("w_map.txt")
    d.update(pairs("map.txt"))
    return d


ERAS = {"Prehistory": "Доисторическая эпоха", "Antiquity": "Древность", "Middle Ages": "Средневековье",
        "Present": "Настоящее", "Future": "Будущее", "End of Time": "Конец Времён",
        "Black Omen": "Чёрное Знамение", "Bonus Areas": "Доп. зоны", "Lost Sanctum": "Забытое святилище",
        "Dimensional Vortex": "Пространственный вихрь", "Time's Eclipse": "Затмение времён"}
MONSTERS = NAMES
