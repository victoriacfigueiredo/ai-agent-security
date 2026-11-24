
from fastapi import FastAPI, Depends, HTTPException
from data.seed import DOCUMENTS
from apis.policy import get_acting_user, can_read_document

app = FastAPI(title="Documents API - Stage 1")


@app.get("/documents")
def get_documents(user: str = Depends(get_acting_user)):
    return [
        document for document in DOCUMENTS
        if can_read_document(user, document)
    ]


@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    user: str = Depends(get_acting_user)
):
    document = next(
        (d for d in DOCUMENTS if d["id"] == document_id),
        None
    )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if not can_read_document(user, document):
        raise HTTPException(status_code=403, detail="Access denied")

    return document
