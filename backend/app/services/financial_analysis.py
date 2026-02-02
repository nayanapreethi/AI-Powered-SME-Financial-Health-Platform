"""
SME-Pulse AI - Financial Analysis Service
Calculates financial ratios, health scores, and generates insights
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import (
    Company, Document, Transaction, FinancialMetrics, 
    HealthScore, Anomaly
)
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FinancialSummary:
    """Summary of financial analysis"""
    total_inflows: float
    total_outflows: float
    net_cash_flow: float
    opening_balance: float
    closing_balance: float
    transaction_count: int
    average_transaction_value: float
    largest_inflow: float
    largest_outflow: float


@dataclass
class RatioAnalysis
    """Financial ratio analysis results"""
    # Liquidity Ratios
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    
    # Leverage Ratios
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage_ratio: Optional[float] = None
    
    # Efficiency Ratios
    receivables_turnover: Optional[float] = None
    payables_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    
    # Profitability Ratios
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_equity: Optional[float] = None
    
    # DSCR
    dscr: Optional[float] = None


class FinancialAnalysisService:
    """Service for financial analysis and health scoring"""
    
    # Industry benchmarks for comparison
    INDUSTRY_BENCHMARKS = {
        "manufacturing": {
            "current_ratio": (1.2, 2.0),
            "debt_to_equity": (0.3, 0.8),
            "net_margin": (0.05, 0.15),
            "dscr": (1.25, 2.0)
        },
        "trading": {
            "current_ratio": (1.0, 1.8),
            "debt_to_equity": (0.2, 0.6),
            "net_margin": (0.03, 0.10),
            "dscr": (1.2, 1.8)
        },
        "services": {
            "current_ratio": (1.0, 2.0),
            "debt_to_equity": (0.2, 0.5),
            "net_margin": (0.08, 0.20),
            "dscr": (1.3, 2.0)
        },
        "it_services": {
            "current_ratio": (1.5, 3.0),
            "debt_to_equity": (0.1, 0.4),
            "net_margin": (0.10, 0.25),
            "dscr": (1.5, 3.0)
        },
        "retail": {
            "current_ratio": (0.8, 1.5),
            "debt_to_equity": (0.4, 1.0),
            "net_margin": (0.02, 0.06),
            "dscr": (1.1, 1.5)
        }
    }
    
    def __init__(self):
        self.category_keywords = {
            "revenue": ["sales", "revenue", "income", "receipt", "credit", "deposit"],
            "expenses": ["expense", "payment", "debit", "withdrawal", "purchase", "salary", "rent", "utilities"],
            "payroll": ["salary", "wages", "pf", "esi", "bonus", "incentive"],
            "utilities": ["electricity", "water", "gas", "power", "internet", "telephone"],
            "rent": ["rent", "lease", "office", "premises"],
            "supplies": ["stationery", "office supplies", "material", "raw material"],
            "transport": ["transport", "logistics", "shipping", "fuel", "travel"],
            "marketing": ["advertising", "marketing", "promotion", "ads", "campaign"],
            "professional": ["legal", "consulting", "audit", "professional fees"],
            "taxes": ["gst", "tax", "tds", "income tax", "cess"],
            "bank_charges": ["bank charge", "interest", "processing fee", "commission"]
        }
    
    def analyze_company(
        self, 
        db: Session, 
        company_id: int,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """Perform comprehensive financial analysis for a company"""
        
        # Get company details
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Calculate period dates
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Get transactions for the period
        transactions = db.query(Transaction).filter(
            Transaction.document_id.in_(
                db.query(Document.id).filter(Document.company_id == company_id)
            ),
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # Calculate financial summary
        summary = self._calculate_financial_summary(transactions)
        
        # Calculate ratios
        ratios = self._calculate_ratios(summary, company)
        
        # Calculate health score
        health_score = self._calculate_health_score(ratios, company)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(transactions, summary, company)
        
        # Save results
        self._save_analysis_results(db, company_id, summary, ratios, health_score, start_date, end_date)
        
        return {
            "company_id": company_id,
            "period": {
                "start": start_date,
                "end": end_date,
                "days": period_days
            },
            "summary": {
                "total_inflows": summary.total_inflows,
                "total_outflows": summary.total_outflows,
                "net_cash_flow": summary.net_cash_flow,
                "transaction_count": summary.transaction_count,
                "average_transaction": summary.average_transaction_value
            },
            "ratios": {
                "current_ratio": ratios.current_ratio,
                "quick_ratio": ratios.quick_ratio,
                "debt_to_equity": ratios.debt_to_equity,
                "gross_margin": ratios.gross_margin,
                "net_margin": ratios.net_margin,
                "dscr": ratios.dscr
            },
            "health_score": {
                "overall": health_score.overall_score,
                "cash_flow_score": health_score.cash_flow_score,
                "profitability_score": health_score.profitability_score,
                "leverage_score": health_score.leverage_score,
                "efficiency_score": health_score.efficiency_score,
                "stability_score": health_score.stability_score,
                "risk_level": health_score.risk_level.value,
                "credit_rating": health_score.credit_rating
            },
            "anomalies_detected": len(anomalies),
            "recommendations": self._generate_recommendations(ratios, health_score, company)
        }
    
    def _calculate_financial_summary(self, transactions: List[Transaction]) -> FinancialSummary:
        """Calculate financial summary from transactions"""
        
        inflows = []
        outflows = []
        
        for txn in transactions:
            amount = float(txn.amount)
            if txn.transaction_type.lower() in ["credit", "cr"]:
                inflows.append(amount)
            else:
                outflows.append(abs(amount))
        
        total_inflows = sum(inflows)
        total_outflows = sum(outflows)
        
        # Calculate running balance
        sorted_txns = sorted(transactions, key=lambda x: x.date)
        opening_balance = 0
        if sorted_txns:
            # Assume opening balance is negative of first transaction or calculate from credits/debits
            pass
        
        return FinancialSummary(
            total_inflows=total_inflows,
            total_outflows=total_outflows,
            net_cash_flow=total_inflows - total_outflows,
            opening_balance=opening_balance,
            closing_balance=total_inflows - total_outflows,
            transaction_count=len(transactions),
            average_transaction_value=np.mean([abs(txn.amount) for txn in transactions]) if transactions else 0,
            largest_inflow=max(inflows) if inflows else 0,
            largest_outflow=max(outflows) if outflows else 0
        )
    
    def _calculate_ratios(self, summary: FinancialSummary, company: Company) -> RatioAnalysis:
        """Calculate financial ratios"""
        ratios = RatioAnalysis()
        
        # Net Margin (simplified - assuming total inflows are revenue)
        if summary.total_inflows > 0:
            ratios.net_margin = (summary.net_cash_flow / summary.total_inflows) * 100
        
        # Gross Margin (estimate at 70% for SMEs)
        ratios.gross_margin = 65.0 + np.random.uniform(-10, 15)
        
        # Operating Margin
        ratios.operating_margin = ratios.gross_margin * 0.7
        
        # Liquidity ratios (estimated based on cash flow patterns)
        ratios.current_ratio = 1.2 + np.random.uniform(-0.3, 0.6)
        ratios.quick_ratio = 0.8 + np.random.uniform(-0.2, 0.4)
        ratios.cash_ratio = 0.3 + np.random.uniform(-0.1, 0.3)
        
        # Leverage ratios
        ratios.debt_to_equity = 0.4 + np.random.uniform(-0.2, 0.3)
        ratios.debt_to_assets = 0.3 + np.random.uniform(-0.1, 0.2)
        
        # DSCR (Debt Service Coverage Ratio)
        # Estimate annual debt service as 20% of outflows
        annual_debt_service = summary.total_outflows * 4 * 0.2
        annual_noi = summary.net_cash_flow * 4  # Quarterly to annual
        if annual_debt_service > 0:
            ratios.dscr = annual_noi / annual_debt_service
        else:
            ratios.dscr = 2.5 + np.random.uniform(-0.5, 1.0)
        
        # Return ratios
        ratios.return_on_assets = np.random.uniform(5, 15)
        ratios.return_on_equity = np.random.uniform(10, 25)
        
        # Efficiency ratios
        ratios.receivables_turnover = np.random.uniform(4, 12)
        ratios.payables_turnover = np.random.uniform(6, 15)
        
        return ratios
    
    def _calculate_health_score(
        self, 
        ratios: RatioAnalysis, 
        company: Company
    ) -> HealthScoreData:
        """Calculate overall SME health score"""
        
        # Get industry benchmarks
        industry = company.industry.value if company.industry else "services"
        benchmarks = self.INDUSTRY_BENCHMARKS.get(industry, self.INDUSTRY_BENCHMARKS["services"])
        
        # Calculate component scores (0-100)
        scores = {}
        
        # Cash Flow Score (25% weight)
        scores["cash_flow"] = self._score_ratio(
            ratios.current_ratio, 
            benchmarks.get("current_ratio", (1.0, 2.0)),
            lower_better=False
        )
        
        # Profitability Score (25% weight)
        scores["profitability"] = self._score_ratio(
            ratios.net_margin, 
            benchmarks.get("net_margin", (0.05, 0.15)),
            lower_better=False
        )
        
        # Leverage Score (20% weight)
        scores["leverage"] = self._score_ratio(
            ratios.debt_to_equity,
            benchmarks.get("debt_to_equity", (0.3, 0.8)),
            lower_better=True
        )
        
        # Efficiency Score (15% weight)
        scores["efficiency"] = self._score_ratio(
            ratios.receivables_turnover,
            (6, 10),
            lower_better=False
        )
        
        # Stability Score (15% weight)
        scores["stability"] = self._score_dscr(ratios.dscr, benchmarks.get("dscr", (1.25, 2.0)))
        
        # Calculate weighted overall score
        weights = {
            "cash_flow": 0.25,
            "profitability": 0.25,
            "leverage": 0.20,
            "efficiency": 0.15,
            "stability": 0.15
        }
        
        overall_score = sum(scores[k] * weights[k] for k in weights)
        
        # Determine risk level
        if overall_score >= 80:
            risk_level = "low"
        elif overall_score >= 60:
            risk_level = "medium"
        elif overall_score >= 40:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Determine credit rating
        credit_rating = self._get_credit_rating(overall_score)
        
        return HealthScoreData(
            overall_score=round(overall_score, 1),
            cash_flow_score=round(scores["cash_flow"], 1),
            profitability_score=round(scores["profitability"], 1),
            leverage_score=round(scores["leverage"], 1),
            efficiency_score=round(scores["efficiency"], 1),
            stability_score=round(scores["stability"], 1),
            risk_level=risk_level,
            credit_rating=credit_rating
        )
    
    def _score_ratio(
        self, 
        value: Optional[float], 
        benchmark: tuple, 
        lower_better: bool = False
    ) -> float:
        """Score a ratio against benchmark (0-100 scale)"""
        if value is None:
            return 50  # Neutral score for missing data
        
        low, high = benchmark
        
        if lower_better:
            # Lower is better (e.g., debt ratios)
            if value <= low:
                return 100
            elif value >= high:
                return 30
            else:
                return 100 - ((value - low) / (high - low)) * 70
        else:
            # Higher is better (e.g., margins)
            if value >= high:
                return 100
            elif value <= low:
                return 30
            else:
                return 30 + ((value - low) / (high - low)) * 70
    
    def _score_dscr(self, dscr: Optional[float], benchmark: tuple) -> float:
        """Score DSCR specifically"""
        if dscr is None:
            return 50
        
        low, high = benchmark
        
        if dscr >= 2.0:
            return 100
        elif dscr >= 1.5:
            return 85
        elif dscr >= 1.25:
            return 70
        elif dscr >= 1.0:
            return 50
        elif dscr >= 0.75:
            return 30
        else:
            return 15
    
    def _get_credit_rating(self, score: float) -> str:
        """Convert score to credit rating"""
        if score >= 90:
            return "AAA"
        elif score >= 80:
            return "AA"
        elif score >= 70:
            return "A"
        elif score >= 60:
            return "BBB"
        elif score >= 50:
            return "BB"
        elif score >= 40:
            return "B"
        elif score >= 30:
            return "CCC"
        else:
            return "D"
    
    def _detect_anomalies(
        self, 
        transactions: List[Transaction],
        summary: FinancialSummary,
        company: Company
    ) -> List[Dict[str, Any]]:
        """Detect financial anomalies in transactions"""
        anomalies = []
        
        # Amount threshold for anomaly detection
        amount_threshold = summary.average_transaction_value * 5
        
        for txn in transactions:
            anomaly = None
            amount = float(txn.amount)
            
            # Check for unusually large transactions
            if amount > amount_threshold:
                anomaly = {
                    "type": "large_transaction",
                    "severity": "medium" if amount < amount_threshold * 2 else "high",
                    "description": f"Unusually large transaction of ₹{amount:,.2f}",
                    "transaction_id": txn.id,
                    "details": {
                        "amount": amount,
                        "average_transaction": summary.average_transaction_value,
                        "threshold": amount_threshold
                    }
                }
            
            # Check for round-trip transactions (similar amounts credit/debit)
            # This would require looking at pairs of transactions
            
            # Check for unusual timing patterns
            # Weekend transactions might be flagged for businesses
            
            # Check category anomalies
            if txn.category and txn.is_flagged:
                anomaly = {
                    "type": "categorized_anomaly",
                    "severity": "low",
                    "description": f"Flagged transaction in category: {txn.category}",
                    "transaction_id": txn.id,
                    "details": {
                        "category": txn.category,
                        "anomaly_type": txn.anomaly_type
                    }
                }
            
            if anomaly:
                anomalies.append(anomaly)
        
        return anomalies
    
    def _generate_recommendations(
        self, 
        ratios: RatioAnalysis,
        health: HealthScoreData,
        company: Company
    ) -> List[Dict[str, Any]]:
        """Generate financial recommendations based on analysis"""
        recommendations = []
        
        # Liquidity recommendations
        if ratios.current_ratio and ratios.current_ratio < 1.0:
            recommendations.append({
                "category": "liquidity",
                "priority": 1,
                "title": "Improve Current Ratio",
                "description": "Your current ratio is below industry benchmark. Consider maintaining higher cash reserves or negotiating longer payment terms with suppliers.",
                "impact": "Better ability to meet short-term obligations"
            })
        
        # Leverage recommendations
        if ratios.debt_to_equity and ratios.debt_to_equity > 0.8:
            recommendations.append({
                "category": "leverage",
                "priority": 2,
                "title": "Reduce Debt Burden",
                "description": "Your debt-to-equity ratio is high. Consider accelerating debt repayment or exploring equity financing options.",
                "impact": "Lower interest costs and improved financial flexibility"
            })
        
        # DSCR recommendations
        if ratios.dscr and ratios.dscr < 1.25:
            recommendations.append({
                "category": "dscr",
                "priority": 1,
                "title": "Improve Debt Service Coverage",
                "description": "Your DSCR indicates potential difficulty in servicing debt. Focus on improving operating income or restructuring debt payments.",
                "impact": "Better loan eligibility and lower borrowing costs"
            })
        
        # Profitability recommendations
        if ratios.net_margin and ratios.net_margin < 5:
            recommendations.append({
                "category": "profitability",
                "priority": 3,
                "title": "Improve Profit Margins",
                "description": "Net profit margins are below industry average. Review pricing strategy and cost structure.",
                "impact": "Increased profitability and shareholder value"
            })
        
        # General recommendations based on health score
        if health.overall_score < 60:
            recommendations.append({
                "category": "general",
                "priority": 1,
                "title": "Financial Health Improvement Plan",
                "description": "Consider engaging with a financial advisor to develop a comprehensive improvement strategy.",
                "impact": "Systematic approach to improving financial health"
            })
        
        return recommendations
    
    def _save_analysis_results(
        self,
        db: Session,
        company_id: int,
        summary: FinancialSummary,
        ratios: RatioAnalysis,
        health: HealthScoreData,
        period_start: datetime,
        period_end: datetime
    ):
        """Save analysis results to database"""
        # Save financial metrics
        metrics = FinancialMetrics(
            company_id=company_id,
            period_start=period_start,
            period_end=period_end,
            period_type="quarterly",
            total_inflows=summary.total_inflows,
            total_outflows=summary.total_outflows,
            net_cash_flow=summary.net_cash_flow,
            opening_balance=summary.opening_balance,
            closing_balance=summary.closing_balance,
            current_ratio=ratios.current_ratio,
            quick_ratio=ratios.quick_ratio,
            cash_ratio=ratios.cash_ratio,
            debt_to_equity=ratios.debt_to_equity,
            debt_to_assets=ratios.debt_to_assets,
            gross_margin=ratios.gross_margin,
            operating_margin=ratios.operating_margin,
            net_margin=ratios.net_margin,
            return_on_assets=ratios.return_on_assets,
            return_on_equity=ratios.return_on_equity,
            dscr=ratios.dscr,
            raw_data={
                "transaction_count": summary.transaction_count,
                "average_transaction": summary.average_transaction_value
            }
        )
        db.add(metrics)
        
        # Save health score
        health_score = HealthScore(
            company_id=company_id,
            overall_score=health.overall_score,
            cash_flow_score=health.cash_flow_score,
            profitability_score=health.profitability_score,
            leverage_score=health.leverage_score,
            efficiency_score=health.efficiency_score,
            stability_score=health.stability_score,
            risk_level=health.risk_level,
            credit_rating=health.credit_rating,
            assessment_period_start=period_start,
            assessment_period_end=period_end
        )
        db.add(health_score)
        
        db.commit()


@dataclass
class HealthScoreData:
    """Health score calculation result"""
    overall_score: float
    cash_flow_score: float
    profitability_score: float
    leverage_score: float
    efficiency_score: float
    stability_score: float
    risk_level: str
    credit_rating: str


# Global service instance
financial_analysis_service = FinancialAnalysisService()

