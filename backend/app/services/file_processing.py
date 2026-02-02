"""
SME-Pulse AI - File Processing Service
Handles PDF, CSV, and XLSX file processing for bank statements and exports
"""

import os
import csv
import io
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
import pdfplumber
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import Document, Transaction, DocumentType

logger = logging.getLogger(__name__)


class FileProcessingService:
    """Service for processing uploaded financial documents"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(self, file, filename: str) -> Path:
        """Save uploaded file to disk"""
        file_path = self.upload_dir / filename
        with open(file_path, "wb") as f:
            f.write(file.read())
        return file_path
    
    def process_document(
        self, 
        db: Session, 
        document_id: int
    ) -> Dict[str, Any]:
        """Process a document and extract transactions"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Update status to processing
        document.status = "processing"
        db.commit()
        
        try:
            # Process based on document type
            if document.document_type == DocumentType.BANK_STATEMENT:
                result = self._process_bank_statement(document)
            elif document.document_type in [DocumentType.TALLY_EXPORT, DocumentType.ZOHO_EXPORT]:
                result = self._process_export_file(document)
            elif document.document_type == DocumentType.GST_RETURN:
                result = self._process_gst_return(document)
            else:
                result = self._extract_generic(document)
            
            # Update document with extracted data
            document.extracted_data = result["data"]
            document.status = "completed"
            
            # Create transaction records
            transactions = result.get("transactions", [])
            for txn_data in transactions:
                transaction = Transaction(
                    document_id=document.id,
                    date=txn_data["date"],
                    description=txn_data.get("description"),
                    amount=txn_data["amount"],
                    transaction_type=txn_data["type"],
                    category=txn_data.get("category"),
                    counterparty=txn_data.get("counterparty"),
                    reference_number=txn_data.get("reference")
                )
                db.add(transaction)
            
            db.commit()
            
            logger.info(f"Successfully processed document {document_id}: {len(transactions)} transactions extracted")
            
            return {
                "status": "success",
                "transactions_extracted": len(transactions),
                "data": result["data"]
            }
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            document.status = "failed"
            document.processing_error = str(e)
            db.commit()
            raise
    
    def _process_bank_statement(self, document: Document) -> Dict[str, Any]:
        """Process bank statement PDF or CSV"""
        file_path = Path(document.file_path)
        
        if file_path.suffix.lower() == ".pdf":
            return self._extract_pdf_transactions(file_path)
        elif file_path.suffix.lower() in [".csv", ".xlsx"]:
            return self._extract_spreadsheet_transactions(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _process_export_file(self, document: Document) -> Dict[str, Any]:
        """Process Tally or Zoho export files"""
        file_path = Path(document.file_path)
        
        if file_path.suffix.lower() == ".csv":
            return self._extract_csv_export(file_path)
        elif file_path.suffix.lower() == ".xlsx":
            return self._extract_xlsx_export(file_path)
        else:
            raise ValueError(f"Unsupported export format: {file_path.suffix}")
    
    def _process_gst_return(self, document: Document) -> Dict[str, Any]:
        """Process GST return data"""
        file_path = Path(document.file_path)
        
        # Extract GST data based on format
        if file_path.suffix.lower() == ".json":
            return self._extract_gst_json(file_path)
        elif file_path.suffix.lower() == ".xlsx":
            return self._extract_xlsx_gst(file_path)
        else:
            # Assume it's a summary PDF
            return self._extract_gst_summary(file_path)
    
    def _extract_pdf_transactions(self, file_path: Path) -> Dict[str, Any]:
        """Extract transactions from bank statement PDF"""
        transactions = []
        extracted_data = {
            "bank_name": None,
            "account_number": None,
            "statement_period": None,
            "opening_balance": None,
            "closing_balance": None
        }
        
        with pdfplumber.open(str(file_path)) as pdf:
            for page in pdf.pages:
                # Extract text and tables
                text = page.extract_text()
                tables = page.extract_tables()
                
                # Parse header information
                if not extracted_data["bank_name"]:
                    extracted_data = self._parse_bank_header(text, extracted_data)
                
                # Process transaction tables
                for table in tables:
                    txns = self._parse_transaction_table(table)
                    transactions.extend(txns)
        
        return {
            "data": extracted_data,
            "transactions": transactions
        }
    
    def _extract_spreadsheet_transactions(self, file_path: Path) -> Dict[str, Any]:
        """Extract transactions from CSV or XLSX"""
        transactions = []
        extracted_data = {}
        
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Normalize column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Extract common fields
        extracted_data = {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
        
        # Map to transaction format
        column_mapping = self._get_column_mapping(list(df.columns))
        
        for _, row in df.iterrows():
            try:
                txn = {
                    "date": pd.to_datetime(row.get(column_mapping.get("date"))),
                    "description": str(row.get(column_mapping.get("description", ""))),
                    "amount": float(row.get(column_mapping.get("amount", 0))),
                    "type": column_mapping.get("type", "debit"),
                    "category": row.get(column_mapping.get("category")),
                    "counterparty": row.get(column_mapping.get("counterparty")),
                    "reference": row.get(column_mapping.get("reference"))
                }
                
                # Determine transaction type based on amount or explicit column
                if "type" in column_mapping:
                    txn["type"] = str(row.get(column_mapping["type"])).lower()
                elif "amount" in column_mapping:
                    amount = txn["amount"]
                    if "balance" in column_mapping.get("amount", ""):
                        # Check balance column to determine credit/debit
                        pass
                    elif amount < 0:
                        txn["type"] = "debit"
                    else:
                        txn["type"] = "credit"
                
                transactions.append(txn)
            except Exception as e:
                logger.warning(f"Failed to parse row: {e}")
                continue
        
        return {
            "data": extracted_data,
            "transactions": transactions
        }
    
    def _extract_csv_export(self, file_path: Path) -> Dict[str, Any]:
        """Extract data from CSV export (Tally/Zoho)"""
        transactions = []
        extracted_data = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        extracted_data = {
            "total_records": len(rows),
            "columns": list(rows[0].keys()) if rows else []
        }
        
        for row in rows:
            try:
                txn = {
                    "date": datetime.strptime(
                        row.get("date", row.get("Date", "")), 
                        "%Y-%m-%d" if len(row.get("date", "")) == 10 else "%d/%m/%Y"
                    ),
                    "description": row.get("description", row.get("Particulars", "")),
                    "amount": float(row.get("amount", row.get("Amount", 0))),
                    "type": "credit" if float(row.get("amount", 0)) > 0 else "debit",
                    "category": row.get("category", row.get("Category", "")),
                    "counterparty": row.get("party", row.get("Ledger", ""))
                }
                transactions.append(txn)
            except Exception as e:
                logger.warning(f"Failed to parse CSV row: {e}")
                continue
        
        return {
            "data": extracted_data,
            "transactions": transactions
        }
    
    def _extract_xlsx_export(self, file_path: Path) -> Dict[str, Any]:
        """Extract data from XLSX export"""
        return self._extract_spreadsheet_transactions(file_path)
    
    def _extract_xlsx_gst(self, file_path: Path) -> Dict[str, Any]:
        """Extract GST data from XLSX"""
        df = pd.read_excel(file_path)
        
        extracted_data = {
            "document_type": "gst_return",
            "total_records": len(df),
            "columns": list(df.columns)
        }
        
        # Extract GST-specific fields
        if "gstin" in df.columns:
            extracted_data["gstin"] = df["gstin"].iloc[0]
        if "tax_period" in df.columns:
            extracted_data["tax_period"] = df["tax_period"].iloc[0]
        
        # Calculate totals
        if "taxable_value" in df.columns:
            extracted_data["total_taxable_value"] = df["taxable_value"].sum()
        if "igst" in df.columns:
            extracted_data["total_igst"] = df["igst"].sum()
        if "cgst" in df.columns:
            extracted_data["total_cgst"] = df["cgst"].sum()
        if "sgst" in df.columns:
            extracted_data["total_sgst"] = df["sgst"].sum()
        
        return {
            "data": extracted_data,
            "transactions": []  # GST returns don't typically have individual transactions
        }
    
    def _extract_gst_json(self, file_path: Path) -> Dict[str, Any]:
        """Extract GST data from JSON"""
        import json
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        extracted_data = {
            "document_type": "gst_return",
            "raw_data": data
        }
        
        return {
            "data": extracted_data,
            "transactions": []
        }
    
    def _extract_gst_summary(self, file_path: Path) -> Dict[str, Any]:
        """Extract GST summary from PDF"""
        with pdfplumber.open(str(file_path)) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages])
        
        # Simple regex-based extraction for common GST fields
        import re
        
        extracted_data = {
            "document_type": "gst_return"
        }
        
        # Extract GSTIN
        gstin_match = re.search(r'GSTIN[:\s]+(\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1})', text)
        if gstin_match:
            extracted_data["gstin"] = gstin_match.group(1)
        
        # Extract tax period
        period_match = re.search(r'Tax Period[:\s]+(\d{2}/\d{4})', text)
        if period_match:
            extracted_data["tax_period"] = period_match.group(1)
        
        return {
            "data": extracted_data,
            "transactions": []
        }
    
    def _extract_generic(self, document: Document) -> Dict[str, Any]:
        """Generic file extraction fallback"""
        file_path = Path(document.file_path)
        
        if file_path.suffix.lower() in [".csv", ".xlsx"]:
            return self._extract_spreadsheet_transactions(file_path)
        else:
            return {
                "data": {"message": "Generic extraction not fully supported for this format"},
                "transactions": []
            }
    
    def _parse_bank_header(self, text: str, extracted_data: Dict) -> Dict:
        """Parse bank statement header for metadata"""
        import re
        
        # Extract bank name (common patterns)
        bank_patterns = [
            r'(ICICI|HDFC|SBI|AXIS|KOTAK|YES BANK|IDFC FIRST|BANDHAN BANK)',
            r'Bank of ([A-Za-z]+)'
        ]
        for pattern in bank_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_data["bank_name"] = match.group(1) if not match.group(0).startswith("Bank of") else f"Bank of {match.group(1)}"
                break
        
        # Extract account number
        acc_pattern = r'Account No[:\s.]*(\d{4,16})'
        acc_match = re.search(acc_pattern, text)
        if acc_match:
            extracted_data["account_number"] = acc_match.group(1)
        
        # Extract statement period
        period_pattern = r'From[:\s]+(\d{2}[/-]\d{2}[/-]\d{4}).*?To[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})'
        period_match = re.search(period_pattern, text, re.DOTALL)
        if period_match:
            try:
                extracted_data["statement_period_start"] = datetime.strptime(
                    period_match.group(1), "%d/%m/%Y" if "/" in period_match.group(1) else "%d-%m-%Y"
                )
                extracted_data["statement_period_end"] = datetime.strptime(
                    period_match.group(2), "%d/%m/%Y" if "/" in period_match.group(2) else "%d-%m-%Y"
                )
            except ValueError:
                pass
        
        return extracted_data
    
    def _parse_transaction_table(self, table: List[List[str]]) -> List[Dict]:
        """Parse a transaction table from PDF"""
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
        
        # Skip header row
        data_rows = table[1:]
        
        for row in data_rows:
            try:
                # Expected columns: Date, Description, Cheque No, Value Date, Withdrawal, Deposit, Balance
                if len(row) >= 4:
                    txn = {
                        "date": self._parse_date(row[0]),
                        "description": row[1] if len(row) > 1 else "",
                        "amount": 0.0,
                        "type": "debit",
                        "category": "uncategorized"
                    }
                    
                    # Parse amounts
                    withdrawal = row[4] if len(row) > 4 else ""
                    deposit = row[5] if len(row) > 5 else ""
                    
                    if withdrawal and float(withdrawal.replace(',', '')) > 0:
                        txn["amount"] = float(withdrawal.replace(',', ''))
                        txn["type"] = "debit"
                    elif deposit and float(deposit.replace(',', '')) > 0:
                        txn["amount"] = float(deposit.replace(',', ''))
                        txn["type"] = "credit"
                    
                    transactions.append(txn)
            except Exception as e:
                logger.warning(f"Failed to parse transaction row: {e}")
                continue
        
        return transactions
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        if not date_str:
            return datetime.utcnow()
        
        date_str = date_str.strip()
        
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d %b %Y",
            "%d %B %Y",
            "%m/%d/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return datetime.utcnow()
    
    def _get_column_mapping(self, columns: List[str]) -> Dict[str, str]:
        """Map column names to standard transaction fields"""
        columns_lower = [c.lower() for c in columns]
        
        mapping = {}
        
        # Date column
        date_candidates = ['date', 'txn date', 'transaction date', 'posting date', 'value date']
        for candidate in date_candidates:
            if candidate in columns_lower:
                mapping["date"] = columns[columns_lower.index(candidate)]
                break
        
        # Description column
        desc_candidates = ['description', ' particulars', 'narration', 'description', 'details', 'memo']
        for candidate in desc_candidates:
            if candidate in columns_lower:
                mapping["description"] = columns[columns_lower.index(candidate)]
                break
        
        # Amount column
        amount_candidates = ['amount', 'txn amount', 'transaction amount', 'value', 'sum']
        for candidate in amount_candidates:
            if candidate in columns_lower:
                mapping["amount"] = columns[columns_lower.index(candidate)]
                break
        
        # Type column
        type_candidates = ['type', 'dr/cr', 'debit/credit', 'transaction type']
        for candidate in type_candidates:
            if candidate in columns_lower:
                mapping["type"] = columns[columns_lower.index(candidate)]
                break
        
        # Category column
        category_candidates = ['category', 'expense category', 'txn category']
        for candidate in category_candidates:
            if candidate in columns_lower:
                mapping["category"] = columns[columns_lower.index(candidate)]
                break
        
        # Counterparty column
        counterparty_candidates = ['counterparty', 'party', 'beneficiary', 'sender', 'payer', 'ledger']
        for candidate in counterparty_candidates:
            if candidate in columns_lower:
                mapping["counterparty"] = columns[columns_lower.index(candidate)]
                break
        
        # Reference column
        ref_candidates = ['reference', 'ref', 'ref no', 'voucher no', 'cheque no', 'utr']
        for candidate in ref_candidates:
            if candidate in columns_lower:
                mapping["reference"] = columns[columns_lower.index(candidate)]
                break
        
        return mapping


# Global service instance
file_processing_service = FileProcessingService()

