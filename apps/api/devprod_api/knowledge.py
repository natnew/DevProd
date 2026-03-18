from __future__ import annotations

import json
import re
from pathlib import Path
from typing import cast

from devprod_api.models import KnowledgeCategory, KnowledgeDocument, RetrievalResult
from devprod_api.repository import ROOT, ScenarioBundle


KNOWLEDGE_ROOT = ROOT / "knowledge"


class KnowledgeRepository:
    def __init__(self, root: Path = KNOWLEDGE_ROOT) -> None:
        self._root = root

    def retrieve(self, bundle: ScenarioBundle) -> RetrievalResult:
        high_signal_paths, distractor_paths = self._parse_retrieval_context(bundle.retrieval_context)
        documents = [doc for path in high_signal_paths if (doc := self._load_document(path)) is not None]
        distractors = [doc for path in distractor_paths if (doc := self._load_document(path)) is not None]

        if not documents:
            documents = self._fallback_documents(bundle)

        coverage_gaps: list[str] = []
        if not documents:
            coverage_gaps.append(
                f"No knowledge documents matched {bundle.incident['service']} and the incident symptom set."
            )
        return RetrievalResult(documents=documents, distractors=distractors, coverageGaps=coverage_gaps)

    def _fallback_documents(self, bundle: ScenarioBundle) -> list[KnowledgeDocument]:
        service = str(bundle.incident.get("service", "")).lower()
        summary = str(bundle.incident.get("summary", "")).lower()
        terms = {term for term in re.findall(r"[a-z0-9-]+", f"{service} {summary}") if len(term) > 3}
        matches: list[KnowledgeDocument] = []
        for relative_path in self._manifest_paths():
            document = self._load_document(relative_path)
            if document is None:
                continue
            corpus = f"{document.title.lower()} {document.excerpt.lower()} {document.path.lower()}"
            if any(term in corpus for term in terms):
                matches.append(document)
        return matches[:4]

    def _manifest_paths(self) -> list[str]:
        manifest_path = self._root / "manifest.json"
        if not manifest_path.exists():
            return []
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        return [str(path) for path in payload.get("documents", [])]

    def _load_document(self, relative_path: str) -> KnowledgeDocument | None:
        normalized = relative_path.strip().strip("`").replace("/", "\\")
        full_path = self._root.parent / normalized
        if not full_path.exists():
            full_path = self._root / normalized
        if not full_path.exists():
            return None

        relative = full_path.relative_to(self._root)
        category = self._normalize_category(relative.parts[0])
        title, excerpt, knowledge_id = self._extract_markdown_metadata(full_path)
        return KnowledgeDocument(
            id=knowledge_id or full_path.stem,
            title=title,
            category=category,
            excerpt=excerpt,
            path=str(full_path.relative_to(self._root.parent)).replace("\\", "/"),
        )

    def _extract_markdown_metadata(self, path: Path) -> tuple[str, str, str | None]:
        text = path.read_text(encoding="utf-8")
        lines = [line.rstrip() for line in text.splitlines()]
        title = path.stem.replace("-", " ").title()
        knowledge_id: str | None = None
        excerpt = ""

        for line in lines:
            if line.startswith("# "):
                title = line.removeprefix("# ").strip()
                break

        for line in lines:
            if line.startswith("Knowledge ID:"):
                knowledge_id = line.split(":", 1)[1].strip()
                break

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or ":" in stripped and not stripped.startswith("`"):
                continue
            excerpt = stripped
            break

        return title, excerpt or title, knowledge_id

    @staticmethod
    def _normalize_category(value: str) -> KnowledgeCategory:
        mapping = {
            "runbooks": "runbook",
            "incidents": "incident",
            "postmortems": "postmortem",
            "architecture": "architecture",
        }
        return cast(KnowledgeCategory, mapping.get(value, value))

    @staticmethod
    def _parse_retrieval_context(text: str | None) -> tuple[list[str], list[str]]:
        if not text:
            return ([], [])

        current: str | None = None
        high_signal: list[str] = []
        distractors: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            lowered = line.lower()
            if lowered.startswith("high-signal documents"):
                current = "docs"
                continue
            if lowered.startswith("plausible distractor"):
                current = "distractors"
                continue
            if not line.startswith("-"):
                continue
            match = re.search(r"`([^`]+)`", line)
            if not match:
                continue
            if current == "docs":
                high_signal.append(match.group(1))
            elif current == "distractors":
                distractors.append(match.group(1))

        return high_signal, distractors
