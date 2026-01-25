#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

RECIPE_ROOT = Path(__file__).resolve().parent.parent / "recettes"

TITLE_PATTERN = re.compile(r"^#\s+(.*)")
META_LINE = re.compile(r"^\*\*(.+?)\*\*\s*:\s*(.*)$")
DURATION_HOURS = re.compile(r"(\d+(?:[\.,]\d+)?)\s*h")
DURATION_MINUTES = re.compile(r"(\d+)\s*min")


@dataclass
class Recipe:
    title: str
    path: Path
    category: str
    prep_minutes: int | None
    cook_minutes: int | None
    tags: list[str]

    @property
    def total_minutes(self) -> int | None:
        if self.prep_minutes is None or self.cook_minutes is None:
            return None
        return self.prep_minutes + self.cook_minutes


def iter_recipe_files() -> Iterable[Path]:
    for path in RECIPE_ROOT.rglob("*.md"):
        if path.name in {"_template-recette.md", "index.md"}:
            continue
        yield path


def parse_duration(text: str) -> int | None:
    hours_match = DURATION_HOURS.search(text)
    minutes_match = DURATION_MINUTES.search(text)
    if not hours_match and not minutes_match:
        return None
    hours = 0.0
    minutes = 0
    if hours_match:
        hours = float(hours_match.group(1).replace(",", "."))
    if minutes_match:
        minutes = int(minutes_match.group(1))
    return int(hours * 60 + minutes)


def parse_recipe(path: Path) -> Recipe:
    text = path.read_text(encoding="utf-8")
    title = path.stem
    prep = None
    cook = None
    tags: list[str] = []
    for line in text.splitlines():
        if title == path.stem:
            title_match = TITLE_PATTERN.match(line)
            if title_match:
                title = title_match.group(1).strip()
        meta_match = META_LINE.match(line)
        if meta_match:
            label = meta_match.group(1).strip().lower()
            value = meta_match.group(2).strip()
            if label == "préparation":
                prep = parse_duration(value)
            elif label == "cuisson":
                cook = parse_duration(value)
            elif label == "tags":
                tags = [tag.strip() for tag in value.split(",") if tag.strip()]
    category = path.relative_to(RECIPE_ROOT).parts[0]
    return Recipe(
        title=title,
        path=path,
        category=category,
        prep_minutes=prep,
        cook_minutes=cook,
        tags=tags,
    )


def format_minutes(total: int) -> str:
    hours = total // 60
    minutes = total % 60
    if hours and minutes:
        return f"{hours} h {minutes} min"
    if hours:
        return f"{hours} h"
    return f"{minutes} min"


def build_index(recipes: list[Recipe]) -> str:
    lines = ["# Index des recettes", ""]

    lines.append("## Par catégorie")
    lines.append("")
    for category in sorted({recipe.category for recipe in recipes}):
        display = category.replace("-", " ").replace("_", " ").title()
        lines.append(f"### {display}")
        for recipe in sorted(
            [r for r in recipes if r.category == category], key=lambda r: r.title.lower()
        ):
            rel_path = recipe.path.relative_to(RECIPE_ROOT)
            lines.append(f"- [{recipe.title}](./{rel_path.as_posix()})")
        lines.append("")

    lines.append("## Par temps total")
    lines.append("")
    total_recipes = [recipe for recipe in recipes if recipe.total_minutes is not None]
    if total_recipes:
        for recipe in sorted(total_recipes, key=lambda r: r.total_minutes or 0):
            rel_path = recipe.path.relative_to(RECIPE_ROOT)
            lines.append(
                f"- {format_minutes(recipe.total_minutes or 0)} — [{recipe.title}](./{rel_path.as_posix()})"
            )
    else:
        lines.append("_Aucun temps total disponible._")
    lines.append("")

    lines.append("## Par tags")
    lines.append("")
    tag_map: dict[str, list[Recipe]] = {}
    for recipe in recipes:
        for tag in recipe.tags:
            tag_map.setdefault(tag, []).append(recipe)
    if tag_map:
        for tag in sorted(tag_map):
            lines.append(f"### {tag}")
            for recipe in sorted(tag_map[tag], key=lambda r: r.title.lower()):
                rel_path = recipe.path.relative_to(RECIPE_ROOT)
                lines.append(f"- [{recipe.title}](./{rel_path.as_posix()})")
            lines.append("")
    else:
        lines.append(
            "_Aucun tag défini. Ajoutez une ligne **Tags** : ... dans les recettes pour activer cette section._"
        )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère un index des recettes")
    parser.parse_args()

    recipes = [parse_recipe(path) for path in iter_recipe_files()]
    content = build_index(recipes)
    target = RECIPE_ROOT / "index.md"
    target.write_text(content, encoding="utf-8")
    print(f"Index généré: {target}")


if __name__ == "__main__":
    main()
