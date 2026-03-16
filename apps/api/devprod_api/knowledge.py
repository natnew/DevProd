import json
from pathlib import Path
from typing import Any, cast

from devprod_api.models import KnowledgeDocument


ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_ROOT = ROOT / "knowledge"


class KnowledgeRepository:
    def __init__(self, root: Path = KNOWLEDGE_ROOT) -> None:
        self._root = root

    def list_for_incident(self) -> list[KnowledgeDocument]:
        return [
            KnowledgeDocument(
                id="runbook-auth-issuer",
                title="Auth Issuer Validation Runbook",
                category="runbook",
                excerpt=(
                    "If authentication failures spike immediately after deployment, verify the "
                    "configured token issuer before rotating keys."
                ),
                path=str(self._root / "runbooks" / "auth-issuer.md"),
            ),
            KnowledgeDocument(
                id="incident-auth-rollback",
                title="Rollback resolved issuer mismatch in checkout",
                category="incident",
                excerpt=self._load_json_summary(self._root / "incidents" / "auth-rollback.json"),
                path=str(self._root / "incidents" / "auth-rollback.json"),
            ),
            KnowledgeDocument(
                id="postmortem-auth-mismatch",
                title="Checkout Auth Mismatch Postmortem",
                category="postmortem",
                excerpt="An environment configuration drift introduced a staging token issuer.",
                path=str(self._root / "postmortems" / "checkout-auth-postmortem.md"),
            ),
            KnowledgeDocument(
                id="architecture-checkout-auth",
                title="Checkout Authentication Architecture",
                category="architecture",
                excerpt="checkout-api validates JWTs using a production issuer.",
                path=str(self._root / "architecture" / "checkout-auth.md"),
            ),
        ]

    @staticmethod
    def _load_json_summary(path: Path) -> str:
        with path.open("r", encoding="utf-8") as handle:
            payload = cast(dict[str, Any], json.load(handle))
        return str(payload["summary"])
