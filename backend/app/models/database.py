"""
SME-Pulse AI - Database Models
SQLAlchemy models for PostgreSQL database
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, 
    Boolean, ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class DocumentType(enum.Enum):
    """Supported document types for upload"""
    BANK_STATEMENT = "bank_statement"
    TALLY_EXPORT = "tally_export"
    ZOHO_EXPORT = "zoho_export"
    GST_RETURN = "gst_return"
    FINANCIAL_REPORT = "financial_report"


class IndustryType(enum.Enum):
    """Industry classifications for SMEs"""
    MANUFACTURING = "manufacturing"
    TRADING = "trading"
    SERVICES = "services"
    CONSTRUCTION = "construction"
    HEALTHCARE = "healthcare"
    IT_SERVICES = "it_services"
    RETAIL = "retail"
    OTHER = "other"


class RiskLevel(enum.Enum):
    """Risk classification levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company_name = Column(String(255))
    phone = Column(String(20))
    industry = Column(SQLEnum(IndustryType))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    companies = relationship("Company", back_populates="owner")
    documents = relationship("Document", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Company(Base):
    """Company/SME profile model"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    industry = Column(SQLEnum(IndustryType))
    registration_number = Column(String(50))
    gst_number = Column(String(20))
    pan_number = Column(String(20))
    address = Column(Text)
    monthly_revenue_estimate = Column(Float)
    employee_count = Column(Integer)
    years_in_business = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="companies")
    documents = relationship("Document", back_populates="company")
    financial_metrics = relationship("FinancialMetrics", back_populates="company")
    health_scores = relationship("HealthScore", back_populates="company")


class Document(Base):
    """Document upload and processing model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    document_type = Column(SQLEnum(DocumentType))
    mime_type = Column(String(100))
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text)
    
    # Extracted data (encrypted)
    extracted_data = Column(JSON)
    
    # Metadata
    bank_name = Column(String(100))
    account_number = Column(String(50))
    statement_period_start = Column(DateTime)
    statement_period_end = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    company = relationship("Company", back_populates="documents")
    transactions = relationship("Transaction", back_populates="document")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_document_user_status', 'user_id', 'status'),
        Index('idx_document_company_type', 'company_id', 'document_type'),
    )


class Transaction(Base):
    """Financial transaction model extracted from documents"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Transaction details
    date = Column(DateTime, nullable=False)
    description = Column(String(500))
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20))  # credit, debit
    
    # Categorization
    category = Column(String(100))
    subcategory = Column(String(100))
    is_flagged = Column(Boolean, default=False)
    anomaly_type = Column(String(100))
    
    # Vendor/Party information
    counterparty = Column(String(255))
    reference_number = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="transactions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_transaction_document_date', 'document_id', 'date'),
        Index('idx_transaction_category', 'category'),
        Index('idx_transaction_flagged', 'is_flagged'),
    )


class FinancialMetrics(Base):
    """Calculated financial metrics for a company"""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Period information
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20))  # monthly, quarterly, yearly
    
    # Cash Flow Metrics
    total_inflows = Column(Float, default=0)
    total_outflows = Column(Float, default=0)
    net_cash_flow = Column(Float, default=0)
    opening_balance = Column(Float, default=0)
    closing_balance = Column(Float, default=0)
    
    # Liquidity Ratios
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    cash_ratio = Column(Float)
    
    # Leverage Ratios
    debt_to_equity = Column(Float)
    debt_to_assets = Column(Float)
    interest_coverage_ratio = Column(Float)
    
    # Efficiency Ratios
    receivables_turnover = Column(Float)
    payables_turnover = Column(Float)
    inventory_turnover = Column(Float)
    
    # Profitability Margins
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)
    return_on_assets = Column(Float)
    return_on_equity = Column(Float)
    
    # DSCR Calculation
    dscr = Column(Float)  # Debt Service Coverage Ratio
    annual_debt_service = Column(Float)
    annual_net_operating_income = Column(Float)
    
    # Raw data snapshot
    raw_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="financial_metrics")
    
    # Indexes
    __table_args__ = (
        Index('idx_financial_metrics_company_period', 'company_id', 'period_start'),
    )


class HealthScore(Base):
    """AI-calculated health score for companies"""
    __tablename__ = "health_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Overall Score (0-100)
    overall_score = Column(Float, nullable=False)
    previous_score = Column(Float)
    score_change = Column(Float)
    
    # Component Scores (0-100)
    cash_flow_score = Column(Float)
    profitability_score = Column(Float)
    leverage_score = Column(Float)
    efficiency_score = Column(Float)
    stability_score = Column(Float)
    
    # Risk Assessment
    risk_level = Column(SQLEnum(RiskLevel))
    risk_factors = Column(JSON)  # List of risk factors identified
    credit_rating = Column(String(20))  # e.g., "AAA", "AA", "A", "BBB", "BB", "B"
    
    # AI Narrative
    narrative_summary = Column(Text)
    recommendations = Column(JSON)  # List of recommendations
    
    # Period
    assessment_period_start = Column(DateTime)
    assessment_period_end = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="health_scores")
    
    # Indexes
    __table_args__ = (
        Index('idx_health_score_company_date', 'company_id', 'created_at'),
    )


class Anomaly(Base):
    """Detected anomalies and irregularities"""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    
    # Anomaly Details
    anomaly_type = Column(String(100), nullable=False)  # round_tripping, unusual_amount, pattern_anomaly
    severity = Column(SQLEnum(RiskLevel), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """AI-generated financial recommendations"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Recommendation Details
    category = Column(String(100))  # cost_optimization, revenue, financing, compliance
    priority = Column(Integer)  # 1=high, 5=low
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    potential_impact = Column(Text)  # Expected benefit
    implementation_steps = Column(JSON)
    
    # Status
    is_implemented = Column(Boolean, default=False)
    implemented_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action Details
    action = Column(String(100), nullable=False)  # upload, view, export, login
    resource_type = Column(String(100))  # document, report, company
    resource_id = Column(Integer)
    
    # Request Information
    ip_address = Column(String(50))
    user_agent = Column(Text)
    request_method = Column(String(10))
    request_path = Column(String(500))
    
    # Additional Data
    metadata = Column(JSON)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_log_user_created', 'user_id', 'created_at'),
        Index('idx_audit_log_action_created', 'action', 'created_at'),
    )

