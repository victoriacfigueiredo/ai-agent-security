from fastapi import FastAPI, Depends, HTTPException
from data.seed import DOCUMENTS
from apis.auth import require_role

app = FastAPI(title="Documents API - Stage 2 OAuth2")


@app.get("/documents")
def get_documents(
    claims: dict = Depends(require_role("documents"))
):
    return DOCUMENTS


@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    claims: dict = Depends(require_role("documents"))
):
    document = next(
        (d for d in DOCUMENTS if d["id"] == document_id),
        None
    )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document
