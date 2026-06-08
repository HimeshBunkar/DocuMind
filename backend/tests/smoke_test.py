from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import health, rag


async def main() -> None:
    status = await health()
    assert status["status"] == "ok"

    content = b"""
    Quarterly security reviews must validate privileged access for every production system.
    Exceptions require written approval and expire within thirty days.

    Priority one incidents require acknowledgement within fifteen minutes and continuous
    remediation updates until the customer-facing service is restored.
    """
    document, preview = await rag.ingest("security-sla-sample.txt", "text/plain", content)
    assert document.status == "ready"
    assert document.chunk_count >= 1
    assert preview

    response = await rag.query(
        question="What does the document say about priority incidents?",
        document_ids=[document.id],
        top_k=3
    )
    assert response.answer
    assert response.citations
    assert response.citations[0].page == 1
    print("backend smoke ok")


if __name__ == "__main__":
    asyncio.run(main())
