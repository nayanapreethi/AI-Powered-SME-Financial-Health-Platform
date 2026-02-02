"""
SME-Pulse AI - Pydantic Schemas
API request and response validation models
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum

from app.models.database import IndustryType, DocumentType, RiskLevel


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)
    industry: Optional[IndustryType] = None
    consent_given: bool = True


class UserResponse(UserBase):
    """Schema for user data in responses"""
    id: int
    industry: Optional[IndustryType]
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== Company Schemas ====================

class CompanyBase(BaseModel):
    """Base company schema"""
    name: str
    industry: Optional[IndustryType] = None
    registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    monthly_revenue_estimate: Optional[float] = None
    employee_count: Optional[int] = None
    years_in_business: Optional[int] = None


class CompanyCreate(CompanyBase):
    """Schema for company creation"""
    pass


class CompanyResponse(CompanyBase):
    """Schema for company data in responses"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Document Schemas ====================

class DocumentUpload(BaseModel):
    """Schema for document upload request"""
    document_type: DocumentType
    company_id: Optional[int] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document data in responses"""
    id: int
    user_id: int
    company_id: Optional[int]
    filename: str
    document_type: DocumentType
    status: str
    bank_name: Optional[str]
    account_number: Optional[str]
    statement_period_start: Optional[datetime]
    statement_period_end: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DocumentProcessingStatus(BaseModel):
    """Schema for document processing status"""
    document_id: int
    status: str  # pending, processing, completed, failed
    progress: int = 0  # Percentage
    message: Optional[str] = None


# ==================== Transaction Schemas ====================

class TransactionBase(BaseModel):
    """Base transaction schema"""
    date: datetime
    description: Optional[str] = None
    amount: float
    transaction_type: str  # credit, debit
    category: Optional[str] = None
    subcategory: Optional[str] = None
    counterparty: Optional[str] = None
    reference_number: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction data in responses"""
    id: int
    document_id: int
    is_flagged: bool
    anomaly_type: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Financial Metrics Schemas ====================

class FinancialMetricsResponse(BaseModel):
    """Schema for financial metrics response"""
    id: int
    company_id: int
    period_start: datetime
    period_end: datetime
    period_type: str
    
    # Cash Flow
    total_inflows: float
    total_outflows: float
    net_cash_flow: float
    opening_balance: float
    closing_balance: float
    
    # Liquidity
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    cash_ratio: Optional[float]
    
    # Leverage
    debt_to_equity: Optional[float]
    interest_coverage_ratio: Optional[float]
    
    # DSCR
    dscr: Optional[float]
    
    # Profitability
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Health Score Schemas ====================

class HealthScoreResponse(BaseModel):
    """Schema for health score response"""
    id: int
    company_id: int
    overall_score: float
    previous_score: Optional[float]
    score_change: Optional[float]
    
    # Component Scores
    cash_flow_score: float
    profitability_score: float
    leverage_score: float
    efficiency_score: float
    stability_score: float
    
    # Risk Assessment
    risk_level: RiskLevel
    risk_factors: List[str]
    credit_rating: Optional[str]
    
    # AI Narrative
    narrative_summary: str
    recommendations: List[dict]
    
    assessment_period_start: datetime
    assessment_period_end: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Anomaly Schemas ====================

class AnomalyResponse(BaseModel):
    """Schema for anomaly data in responses"""
    id: int
    company_id: int
    anomaly_type: str
    severity: RiskLevel
    description: str
    details: Optional[dict]
    is_resolved: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AnomalyListResponse(BaseModel):
    """Schema for anomaly list response"""
    anomalies: List[AnomalyResponse]
    total: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


# ==================== AI Narrative Schemas ====================

class CashFlowNarrativeRequest(BaseModel):
    """Request for cash flow narrative generation"""
    company_id: int
    period_days: int = 30


class CashFlowNarrativeResponse(BaseModel):
    """Response with AI-generated cash flow narrative"""
    company_id: int
    period: str
    summary: str
    key_insights: List[str]
    highlights: List[str]
    concerns: List[str]
    recommendations: List[str]


class FinancialAdvisoryRequest(BaseModel):
    """Request for financial advisory"""
    company_id: int
    focus_areas: List[str] = ["cost_optimization", "cash_flow", "growth"]


class FinancialAdvisoryResponse(BaseModel):
    """Response with AI-generated financial advisory"""
    company_id: int
    advisory_type: str
    summary: str
    recommendations: List[dict]
    potential_savings: Optional[float]
    growth_opportunities: List[dict]


# ==================== Product Recommendation Schemas ====================

class ProductRecommendationRequest(BaseModel):
    """Request for product recommendations"""
    company_id: int


class ProductRecommendationResponse(BaseModel):
    """Response with financial product recommendations"""
    company_id: int
    recommendations: List[dict]
    qualified_products: List[dict]
    pre_qualification_status: str


# ==================== Report Schemas ====================

class ReportGenerateRequest(BaseModel):
    """Request for report generation"""
    company_id: int
    report_type: str  # investor_ready, credit_assessment, tax_compliance
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class ReportResponse(BaseModel):
    """Response for generated report"""
    report_id: int
    report_type: str
    download_url: str
    expires_at: datetime
    pages: int


# ==================== Dashboard Schemas ====================

class DashboardSummary(BaseModel):
    """Dashboard summary response"""
    company_id: int
    company_name: str
    
    # Health Score
    overall_score: float
    score_trend: str  # improving, stable, declining
    
    # Key Metrics
    current_ratio: Optional[float]
    dscr: Optional[float]
    net_margin: Optional[float]
    
    # Period Comparison
    period_revenue_change: float
    period_profit_change: float
    
    # Alerts
    anomaly_count: int
    unresolved_anomalies: int
    compliance_alerts: int
    
    # Recent Activity
    last_document_upload: Optional[datetime]
    last_analysis_date: Optional[datetime]


# ==================== Common Schemas ====================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

