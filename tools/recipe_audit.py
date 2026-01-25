#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

RECIPE_ROOT = Path(__file__).resolve().parent.parent / "recettes"
OPTIONAL_SECTIONS = ["Conseils / astuces", "Suggestions de service"]
REQUIRED_SECTIONS = ["Ingrédients", "Préparation"]
IMAGE_PLACEHOLDER = "CHEMIN/VERS-IMAGE"

IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SECTION_PATTERN = re.compile(r"^##\s+(.*)\s*$")
META_QUANTITE = re.compile(r"^\*\*Quantité\*\*\s*:", re.IGNORECASE)
META_RENDEMENT = re.compile(r"^\*\*Rendement\*\*\s*:", re.IGNORECASE)


@dataclass
class Issue:
    level: str  # "error" or "warning"
    message: str
    file: Path | None = None


@dataclass
class RecipeInfo:
    path: Path
    category: str
    slug: str


@dataclass
class AuditSummary:
    recipes_checked: int
    recipes_conforming: int
    errors: list[Issue]
    warnings: list[Issue]


class RecipeAudit:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[Issue] = []
        self.warnings: list[Issue] = []

    def run(self, fix: bool = False) -> AuditSummary:
        if fix:
            self._apply_fixes()

        recipe_files = list(self._iter_recipe_files())
        for recipe in recipe_files:
            self._audit_recipe(recipe)

        recipes_conforming = 0
        for recipe in recipe_files:
            if not any(issue.file == recipe and issue.level == "error" for issue in self.errors):
                recipes_conforming += 1

        return AuditSummary(
            recipes_checked=len(recipe_files),
            recipes_conforming=recipes_conforming,
            errors=self.errors,
            warnings=self.warnings,
        )

    def _apply_fixes(self) -> None:
        self._rename_missing_extensions()
        for recipe in self._iter_recipe_files():
            self._fix_metadata(recipe)
            self._ensure_sections(recipe)

    def _rename_missing_extensions(self) -> None:
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if path.suffix:
                continue
            if path.name.startswith("."):
                continue
            new_path = path.with_suffix(".md")
            if new_path.exists():
                continue
            path.rename(new_path)

    def _fix_metadata(self, path: Path) -> None:
        category = self._category_for(path)
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        updated_lines = []
        changed = False
        for line in text.splitlines():
            new_line = line
            if META_QUANTITE.match(line):
                if category == "sauces":
                    new_line = re.sub(r"\*\*Quantité\*\*", "**Rendement**", line)
                else:
                    new_line = re.sub(r"\*\*Quantité\*\*", "**Personnes**", line)
                changed = True
            elif META_RENDEMENT.match(line) and category != "sauces":
                new_line = re.sub(r"\*\*Rendement\*\*", "**Personnes**", line)
                changed = True
            updated_lines.append(new_line)
        if changed:
            path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    def _ensure_sections(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        sections = self._extract_sections(text)
        missing = [section for section in REQUIRED_SECTIONS + OPTIONAL_SECTIONS if section not in sections]
        if not missing:
            return
        additions = []
        for section in missing:
            additions.append("---")
            additions.append("")
            additions.append(f"## {section}")
            additions.append("")
            if section == "Préparation":
                additions.append("1. TODO")
            else:
                additions.append("- TODO")
            additions.append("")
        updated = text.rstrip() + "\n\n" + "\n".join(additions)
        path.write_text(updated + "\n", encoding="utf-8")

    def _iter_recipe_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if path.name in {"_template-recette.md", "index.md"}:
                continue
            if path.suffix == ".md":
                yield path

    def _audit_recipe(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        if IMAGE_PLACEHOLDER in text:
            self.errors.append(Issue("error", f"Placeholder d'image détecté: {IMAGE_PLACEHOLDER}", path))

        self._check_sections(path, text)
        self._check_images(path, text)
        self._check_expected_image(path)

    def _check_sections(self, path: Path, text: str) -> None:
        sections = self._extract_sections(text)
        for section in REQUIRED_SECTIONS:
            if section not in sections:
                self.errors.append(Issue("error", f"Section manquante: {section}", path))
        for section in OPTIONAL_SECTIONS:
            if section not in sections:
                self.warnings.append(Issue("warning", f"Section optionnelle manquante: {section}", path))

    def _check_images(self, path: Path, text: str) -> None:
        for match in IMAGE_PATTERN.finditer(text):
            raw_target = match.group(1).strip()
            target = raw_target.split()[0]
            if target.startswith("http://") or target.startswith("https://"):
                continue
            if target.startswith("mailto:"):
                continue
            target_path = (path.parent / target).resolve()
            if not target_path.exists():
                self.errors.append(Issue("error", f"Image introuvable: {target}", path))

    def _check_expected_image(self, path: Path) -> None:
        info = self._recipe_info(path)
        if not info:
            return
        expected = Path("..") / ".." / "images" / info.category / f"{info.slug}-hero.jpg"
        text = path.read_text(encoding="utf-8")
        images = [match.group(1).strip().split()[0] for match in IMAGE_PATTERN.finditer(text)]
        if images and images[0] != str(expected):
            self.warnings.append(
                Issue(
                    "warning",
                    f"Image principale non conforme. Attendu: {expected}",
                    path,
                )
            )
        if not images:
            self.warnings.append(Issue("warning", "Aucune image détectée", path))

    def _recipe_info(self, path: Path) -> RecipeInfo | None:
        try:
            relative = path.relative_to(self.root)
        except ValueError:
            return None
        parts = relative.parts
        if len(parts) < 2:
            return None
        category = parts[0]
        slug = path.stem
        return RecipeInfo(path=path, category=category, slug=slug)

    def _category_for(self, path: Path) -> str:
        info = self._recipe_info(path)
        return info.category if info else ""

    def _extract_sections(self, text: str) -> set[str]:
        sections = set()
        for line in text.splitlines():
            match = SECTION_PATTERN.match(line)
            if match:
                sections.add(match.group(1).strip())
        return sections

    def check_non_md_files(self) -> None:
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if path.name in {"_template-recette.md", "index.md"}:
                continue
            if path.suffix != ".md":
                self.errors.append(Issue("error", "Fichier non .md dans recettes/", path))

    def report(self, summary: AuditSummary) -> int:
        total_errors = len(summary.errors)
        total_warnings = len(summary.warnings)

        print("=== Audit des recettes ===")
        print(f"Recettes analysées : {summary.recipes_checked}")
        print(f"Recettes conformes  : {summary.recipes_conforming}")
        print(f"Erreurs bloquantes  : {total_errors}")
        print(f"Warnings            : {total_warnings}")
        print("")

        if summary.errors:
            print("Erreurs:")
            for issue in summary.errors:
                location = f" ({issue.file.relative_to(self.root)})" if issue.file else ""
                print(f"- {issue.message}{location}")
            print("")

        if summary.warnings:
            print("Warnings:")
            for issue in summary.warnings:
                location = f" ({issue.file.relative_to(self.root)})" if issue.file else ""
                print(f"- {issue.message}{location}")
            print("")

        warning_counter = Counter(issue.message for issue in summary.warnings)
        if warning_counter:
            print("Top 5 warnings:")
            for message, count in warning_counter.most_common(5):
                print(f"- {message} ({count})")
            print("")

        expected_images = self._expected_images()
        if expected_images:
            print("Images attendues (convention):")
            for recipe_path, expected in expected_images:
                relative = recipe_path.relative_to(self.root)
                print(f"- {relative}: {expected.as_posix()}")
            print("")

        return 1 if total_errors > 0 else 0

    def run_full(self, fix: bool = False) -> int:
        if fix:
            self._apply_fixes()
        self.check_non_md_files()
        summary = self.run(fix=False)
        return self.report(summary)

    def _expected_images(self) -> list[tuple[Path, Path]]:
        expected = []
        for recipe in self._iter_recipe_files():
            info = self._recipe_info(recipe)
            if not info:
                continue
            expected_path = Path("images") / info.category / f"{info.slug}-hero.jpg"
            expected.append((recipe, expected_path))
        return expected


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit des recettes")
    parser.add_argument("--fix", action="store_true", help="Corriger automatiquement les cas simples")
    args = parser.parse_args()

    audit = RecipeAudit(RECIPE_ROOT)
    exit_code = audit.run_full(fix=args.fix)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
