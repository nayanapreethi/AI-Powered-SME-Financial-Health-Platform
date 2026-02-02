"""
SME-Pulse AI - Financial Analysis API Routes
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.database import User, Company, HealthScore, FinancialMetrics, Anomaly
from app.schemas.schemas import (
    HealthScoreResponse, FinancialMetricsResponse, AnomalyListResponse,
    CashFlowNarrativeRequest, CashFlowNarrativeResponse, FinancialAdvisoryRequest,
    FinancialAdvisoryResponse, DashboardSummary, MessageResponse
)
from app.services.financial_analysis import financial_analysis_service
from app.services.ai_narrative import ai_narrative_service

router = APIRouter(prefix="/analysis", tags=["Analysis"])


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


def get_company(company_id: int, user_id: int, db: Session):
    """Get company and verify ownership"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == user_id
    ).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.post("/health-score/{company_id}")
def calculate_health_score(
    company_id: int,
    period_days: int = Query(90, ge=30, le=365),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Calculate and generate comprehensive health score for a company.
    This analyzes all uploaded financial data and calculates:
    - Overall health score (0-100)
    - Component scores (cash flow, profitability, leverage, efficiency, stability)
    - Risk level and credit rating
    - AI-generated narrative and recommendations
    """
    
    user = get_current_user(token, db)
    company = get_company(company_id, user.id, db)
    
    # Perform analysis
    try:
        analysis_result = financial_analysis_service.analyze_company(
            db=db,
            company_id=company_id,
            period_days=period_days
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # Get the latest health score from database
    health_score = db.query(HealthScore).filter(
        HealthScore.company_id == company_id
    ).order_by(HealthScore.created_at.desc()).first()
    
    if not health_score:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health score calculation failed"
        )
    
    return HealthScoreResponse.model_validate(health_score)


@router.get("/health-score/{company_id}", response_model=HealthScoreResponse)
def get_health_score(
    company_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get the latest health score for a company"""
    
    user = get_current_user(token, db)
    company = get_company(company_id, user.id, db)
    
    health_score = db.query(HealthScore).filter(
        HealthScore.company_id == company_id
    ).order_by(HealthScore.created_at.desc()).first()
    
    if not health_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health score available. Please run analysis first."
        )
    
    return HealthScoreResponse.model_validate(health_score)


@router.get("/health-score/{company_id}/history")
def get_health_score_history(
    company_id: int,
    limit: int = Query(10, ge=1, le=50),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get historical health scores for a company"""
    
    user = get_current_user(token, db)
    company = get_company(company_id, user.id, db)
    
    scores = db.query(HealthScore).filter(
        HealthScore.company_id == company_id
    ).order_by(HealthScore.created_at.desc()).limit(limit).all()
    
    return {
        "company_id": company_id,
        "history": [
            {
                "date": score.created_at.isoformat(),
                "overall_score": score.overall_score,
                "cash_flow_score": score.cash_flow_score,
                "profitability_score": score.profitability_score,
                "leverage_score": score.leverage_score,
                "risk_level": score.risk_level.value,
                "credit_rating": score.credit_rating
            }
            for score in scores
        ]
    }


@router.get("/financial-metrics/{company_id}", response_model=FinancialMetricsResponse)
def get_financial_metrics(
    company_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get latest financial metrics for a company"""
    
    user = get_current_user(token, db)
    company = get_company(company_id, user.id, db)
    
    metrics = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id
    ).order_by(FinancialMetrics.created_at.desc()).first()
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial metrics available. Please run analysis first."
        )
    
    return FinancialMetricsResponse.model_validate(metrics)


@router.get("/anomalies/{company_id}", response_model=AnomalyListResponse)
def get_anomalies(
    company_id: int,
    severity: Optional[str] = Query(None),
    include_resolved: bool = Query(False),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get detected financial anomalies for a company"""
    
    user = get_current_user(token, db)
    company = get_company(company_id, user.id, db)
    
    query = db.query(Anomaly).filter(Anomaly.company_id == company_id)
    
    if not include_resolved:
        query = query.filter(Anomaly.is_resolved == False)
    
    if severity:
        query = query.filter(Anomaly.severity == severity)
    
    anomalies = query.order_by(Anomaly.created_at.desc()).all()
    
    # Count by severity
    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    for anomaly in anomalies:
        counts[anomaly.severity.value] += 1
    
    return AnomalyListResponse(
        anomalies=[{
            "id": a.id,
            "company_id": a.company_id,
            "anomaly_type": a.anomaly_type,
            "severity": a.severity.value,
            "description": a.description,
            "details": a.details,
            "is_resolved": a.is_resolved,
            "created_at": a.created_at.isoformat()
        } for a in anomalies],
        total=len(anomalies),
        **counts
    )


@router.post("/cash-flow-narrative", response_model=CashFlowNarrativeResponse)
def generate_cash_flow_narrative(
    request: CashFlowNarrativeRequest,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Generate AI-powered cash flow narrative"""
    
    user = get_current_user(token, db)
    company = get_company(request.company_id, user.id, db)
    
    narrative = ai_narrative_service.generate_cash_flow_narrative(
        db=db,
        company_id=request.company_id,
        period_days=request.period_days
    )
    
    return CashFlowNarrativeResponse(
        company_id=request.company_id,
        period=f"Last {request.period_days} days",
        summary=narrative.summary,
        key_insights=narrative.key_insights,
        highlights=narrative.highlights,
        concerns=narrative.concerns,
        recommendations=narrative.recommendations
    )


@router.post("/financial-advisory", response_model=FinancialAdvisoryResponse)
def generate_financial_advisory(
    request: FinancialAdvisoryRequest,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Generate AI-powered financial advisory recommendations"""
    
    user = get_current_user(token, db)
    company = get_company(request.company_id, user.id, db)
    
    advisory = ai_narrative_service.generate_financial_advisory(
        db=db,
        company_id=request.company_id,
        focus_areas=request.focus_areas
    )
    
    return FinancialAdvisoryResponse(
        company_id=request.company_id,
        advisory_type="comprehensive",
        summary=advisory.summary,
        recommendations=advisory.recommendations,
        potential_savings=advisory.potential_savings,
        growth_opportunities=advisory.growth_opportunities
    )


@router.get("/dashboard/{company_id}", response_model=DashboardSummary)
def get_dashboard_summary(
    company_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get dashboard summary for a company"""
    
    user = get_current_user(token, db)
    company = get_company(company_id, user.id, db)
    
    # Get latest health score
    health_score = db.query(HealthScore).filter(
        HealthScore.company_id == company_id
    ).order_by(HealthScore.created_at.desc()).first()
    
    # Get latest financial metrics
    metrics = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id
    ).order_by(FinancialMetrics.created_at.desc()).first()
    
    # Get anomaly count
    anomaly_count = db.query(Anomaly).filter(
        Anomaly.company_id == company_id,
        Anomaly.is_resolved == False
    ).count()
    
    # Calculate score trend (compare with previous score)
    if health_score:
        previous_score = health_score.previous_score
        if previous_score:
            if health_score.overall_score > previous_score:
                score_trend = "improving"
            elif health_score.overall_score < previous_score:
                score_trend = "declining"
            else:
                score_trend = "stable"
        else:
            score_trend = "stable"
    else:
        score_trend = "stable"
        health_score = type('obj', (object,), {
            'overall_score': None,
            'cash_flow_score': None,
            'dscr': None,
            'net_margin': None
        })()
    
    # Get last activity dates
    from app.models.database import Document
    last_upload = db.query(Document).filter(
        Document.company_id == company_id
    ).order_by(Document.created_at.desc()).first()
    
    return DashboardSummary(
        company_id=company_id,
        company_name=company.name,
        overall_score=health_score.overall_score,
        score_trend=score_trend,
        current_ratio=metrics.current_ratio if metrics else None,
        dscr=health_score.cash_flow_score if health_score else None,
        net_margin=metrics.net_margin if metrics else None,
        period_revenue_change=0.0,  # Would calculate from comparison
        period_profit_change=0.0,
        anomaly_count=anomaly_count,
        unresolved_anomalies=anomaly_count,
        compliance_alerts=0,
        last_document_upload=last_upload.created_at if last_upload else None,
        last_analysis_date=health_score.created_at if health_score else None
    )


@router.post("/products/recommendations")
def get_product_recommendations(
    company_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get financial product recommendations based on company profile"""
    
    user = get_current_user(token, db)
    company = get_company(company_id, user.id, db)
    
    # Get latest health score
    health_score = db.query(HealthScore).filter(
        HealthScore.company_id == company_id
    ).order_by(HealthScore.created_at.desc()).first()
    
    if not health_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please run health assessment first to get product recommendations"
        )
    
    # Generate mock recommendations based on health score
    recommendations = []
    
    if health_score.overall_score >= 60:
        recommendations.append({
            "product": "Working Capital Loan",
            "provider": "Multiple Banks",
            "eligibility": "Eligible",
            "amount": "Up to ₹1 Crore",
            "interest_rate": "From 10.5% p.a.",
            "tenure": "12-36 months",
            "use_case": "Business expansion, inventory, operational expenses"
        })
        
        recommendations.append({
            "product": "Invoice Discounting",
            "provider": "NBFCs & Banks",
            "eligibility": "Eligible",
            "amount": "Up to 80% of invoice value",
            "interest_rate": "From 12% p.a.",
            "tenure": "30-90 days",
            "use_case": "Faster access to tied-up capital"
        })
    
    if health_score.overall_score >= 70:
        recommendations.append({
            "product": "Equipment Financing",
            "provider": "Banks & NBFCs",
            "eligibility": "Highly Eligible",
            "amount": "Up to ₹2 Crore",
            "interest_rate": "From 11% p.a.",
            "tenure": "24-60 months",
            "use_case": "Machinery, vehicles, technology"
        })
    
    # Credit card recommendation
    recommendations.append({
        "product": "Business Credit Card",
        "provider": "Multiple Banks",
        "eligibility": "Available",
        "amount": "₹5-50 Lakh limit",
        "interest_rate": "From 3.5% p.m.",
        "tenure": "Revolving",
        "use_case": "Day-to-day expenses, cash flow management"
    })
    
    return {
        "company_id": company_id,
        "health_score": health_score.overall_score,
        "credit_rating": health_score.credit_rating,
        "recommendations": recommendations,
        "pre_qualification_status": "qualified" if health_score.overall_score >= 60 else "needs_improvement"
    }

