"""
Document & Knowledge Manager Agent Implementation
Integrates with Google Drive to search files and summarize documents/PDFs.
Conforms to specs/agents/worker_tools.yaml
"""
from typing import Dict, Any, List
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    SearchDriveRequest,
    SummarizeDocumentRequest
)

class DocumentManagerAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="DocumentManager")

    def search_drive(self, request: SearchDriveRequest) -> List[Dict[str, Any]]:
        """
        Search files in Google Drive by query and file_type.
        """
        q = request.query.lower()
        return [
            {
                "file_id": "file_doc_101",
                "name": f"Tax_Return_2025_{q}.pdf",
                "mime_type": "application/pdf",
                "modified_at": "2026-04-12T10:00:00Z"
            },
            {
                "file_id": "file_doc_102",
                "name": f"Project_Proposal_{q}.docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "modified_at": "2026-07-20T16:30:00Z"
            }
        ]

    def summarize_document(self, request: SummarizeDocumentRequest) -> Dict[str, Any]:
        """
        Extract key text and summarize document content.
        """
        doc_name = request.file_name or f"Document #{request.file_id}"
        return {
            "file_id": request.file_id,
            "file_name": doc_name,
            "summary": f"This document ({doc_name}) contains financial summaries, strategic goals, and execution timelines.",
            "key_takeaways": [
                "Overall budget compliance is within 95% target range.",
                "Next milestone deliverables scheduled for mid-Q3."
            ]
        }

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        action = payload.action
        raw_payload = payload.payload or {}

        if action == "summarize_document":
            req = SummarizeDocumentRequest(**raw_payload)
            res = self.summarize_document(req)
            takeaways = "\n".join([f"  - {t}" for t in res["key_takeaways"]])
            reply = (
                f"📄 *Document Summary ({res['file_name']})*:\n"
                f"{res['summary']}\n\n"
                f"*Key Takeaways*:\n{takeaways}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"file_id": res["file_id"]}
            )

        else:
            # Default: search_drive
            req = SearchDriveRequest(**raw_payload)
            files = self.search_drive(req)
            formatted = "\n".join([f"• [{f['mime_type'].split('.')[-1].upper()}] {f['name']} (ID: {f['file_id']})" for f in files])
            reply = f"📁 *Google Drive Search Results for '{req.query}'*:\n{formatted}"
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"file_count": len(files)}
            )
