"""
SME-Pulse AI - Document Management API Routes
"""

import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.config import settings
from app.models.database import User, Document, Company, Transaction, DocumentType
from app.schemas.schemas import (
    DocumentUpload, DocumentResponse, DocumentProcessingStatus,
    TransactionListResponse, TransactionResponse, MessageResponse
)
from app.services.file_processing import file_processing_service

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user from token"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Query(...),
    company_id: Optional[int] = Query(None),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Upload a financial document (PDF/CSV/XLSX)"""
    
    user = get_current_user(token, db)
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = settings.UPLOAD_DIR / unique_filename
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record
    document = Document(
        user_id=user.id,
        company_id=company_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        document_type=document_type,
        mime_type=file.content_type,
        status="pending"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Start async processing (in production, would use Celery)
    try:
        result = file_processing_service.process_document(db, document.id)
    except Exception as e:
        document.status = "failed"
        document.processing_error = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )
    
    return DocumentResponse.model_validate(document)


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    company_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """List user's documents"""
    
    user = get_current_user(token, db)
    
    query = db.query(Document).filter(Document.user_id == user.id)
    
    if company_id:
        query = query.filter(Document.company_id == company_id)
    
    if status_filter:
        query = query.filter(Document.status == status_filter)
    
    documents = query.order_by(Document.created_at.desc()).all()
    
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get document details"""
    
    user = get_current_user(token, db)
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/transactions", response_model=TransactionListResponse)
def get_document_transactions(
    document_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get transactions extracted from a document"""
    
    user = get_current_user(token, db)
    
    # Verify document ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get transactions
    offset = (page - 1) * page_size
    transactions = db.query(Transaction).filter(
        Transaction.document_id == document_id
    ).offset(offset).limit(page_size).all()
    
    total = db.query(Transaction).filter(
        Transaction.document_id == document_id
    ).count()
    
    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(
    document_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Delete a document and its associated transactions"""
    
    user = get_current_user(token, db)
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file
    try:
        os.remove(document.file_path)
    except OSError:
        pass  # File might already be deleted
    
    # Delete transactions
    db.query(Transaction).filter(Transaction.document_id == document_id).delete()
    
    # Delete document
    db.delete(document)
    db.commit()
    
    return MessageResponse(message="Document deleted successfully")


@router.get("/{document_id}/status", response_model=DocumentProcessingStatus)
def get_processing_status(
    document_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get document processing status"""
    
    user = get_current_user(token, db)
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Calculate progress based on status
    progress = {
        "pending": 0,
        "processing": 50,
        "completed": 100,
        "failed": 100
    }.get(document.status, 0)
    
    return DocumentProcessingStatus(
        document_id=document_id,
        status=document.status,
        progress=progress,
        message=document.processing_error
    )

