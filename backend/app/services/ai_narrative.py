"""
SME-Pulse AI - AI Narrative Service
Generates financial narratives and insights using Claude/GPT (mock responses for demo)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.database import Company, FinancialMetrics, HealthScore, Transaction
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CashFlowNarrative:
    """Generated cash flow narrative"""
    summary: str
    key_insights: List[str]
    highlights: List[str]
    concerns: List[str]
    recommendations: List[str]


@dataclass
class FinancialAdvisory:
    """Financial advisory recommendations"""
    summary: str
    recommendations: List[Dict[str, Any]]
    potential_savings: float
    growth_opportunities: List[Dict[str, Any]]


class AINarrativeService:
    """Service for generating AI-powered financial narratives and insights"""
    
    def __init__(self):
        self.enabled = settings.AI_API_KEY is not None
        self.model = settings.AI_MODEL
    
    def generate_cash_flow_narrative(
        self,
        db: Session,
        company_id: int,
        period_days: int = 30
    ) -> CashFlowNarrative:
        """Generate AI-powered cash flow narrative"""
        
        # Get company and financial data
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Get latest health score
        latest_score = db.query(HealthScore).filter(
            HealthScore.company_id == company_id
        ).order_by(HealthScore.created_at.desc()).first()
        
        # Get transactions for period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        transactions = db.query(Transaction).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # Calculate basic metrics
        total_inflows = sum(t.amount for t in transactions if t.transaction_type.lower() in ['credit', 'cr'])
        total_outflows = sum(abs(t.amount) for t in transactions if t.transaction_type.lower() in ['debit', 'dr'])
        net_flow = total_inflows - total_outflows
        
        # Generate narrative based on mock AI (in production, would call Claude/GPT)
        return self._generate_mock_narrative(
            company_name=company.name,
            total_inflows=total_inflows,
            total_outflows=total_outflows,
            net_flow=net_flow,
            transaction_count=len(transactions),
            health_score=latest_score,
            period_days=period_days
        )
    
    def _generate_mock_narrative(
        self,
        company_name: str,
        total_inflows: float,
        total_outflows: float,
        net_flow: float,
        transaction_count: int,
        health_score: Optional[HealthScore],
        period_days: int
    ) -> CashFlowNarrative:
        """Generate mock narrative for demonstration"""
        
        # Determine flow direction
        if net_flow > 0:
            flow_status = "positive cash flow"
            flow_emoji = "📈"
        elif net_flow < 0:
            flow_status = "negative cash flow"
            flow_emoji = "📉"
        else:
            flow_status = "balanced cash flow"
            flow_emoji = "⚖️"
        
        # Generate summary
        summary = f"""
{flow_emoji} **{company_name}** has demonstrated {flow_status} over the past {period_days} days.

**Key Highlights:**
• Total inflows: ₹{total_inflows:,.2f}
• Total outflows: ₹{total_outflows:,.2f}
• Net cash movement: ₹{net_flow:,.2f}
• Transaction volume: {transaction_count} transactions

**Overall Assessment:** {'Healthy' if health_score and health_score.overall_score >= 60 else 'Needs Attention'}
"""
        
        # Key insights
        insights = []
        
        if health_score:
            if health_score.cash_flow_score >= 70:
                insights.append("Strong cash generation capacity with consistent inflows")
            else:
                insights.append("Cash flow consistency needs improvement")
            
            if health_score.profitability_score >= 70:
                insights.append("Profitability metrics are above industry average")
            else:
                insights.append("Margin compression observed in recent periods")
            
            if health_score.leverage_score >= 70:
                insights.append("Conservative debt levels provide financial flexibility")
            else:
                insights.append("High debt levels may constrain growth options")
        
        # Inflow/outflow specific insights
        if total_inflows > 0:
            avg_inflow = total_inflows / max(1, len([t for t in range(1) if True]))
            insights.append(f"Average daily inflow: ₹{total_inflows/period_days:,.2f}")
        
        # Highlights
        highlights = []
        if net_flow > 0:
            highlights.append(f"Net surplus of ₹{net_flow:,.2f} generated")
            highlights.append("Sufficient buffer for operational expenses")
        else:
            highlights.append(f"Net deficit of ₹{abs(net_flow):,.2f} recorded")
            highlights.append("May need to rely on credit facilities")
        
        if transaction_count > 50:
            highlights.append("High transaction volume indicates active operations")
        elif transaction_count < 10:
            highlights.append("Low transaction volume - seasonal patterns or reduced activity")
        
        # Concerns
        concerns = []
        if net_flow < 0:
            concerns.append("Continuous outflows exceed inflows - unsustainable without external funding")
        if health_score and health_score.risk_level.value in ['high', 'critical']:
            concerns.append("Elevated risk profile requires immediate attention")
        if total_outflows > total_inflows * 1.2:
            concerns.append("Expense growth outpacing revenue growth")
        if transaction_count == 0:
            concerns.append("No transactions recorded - please verify data upload")
        
        # Recommendations
        recommendations = []
        if net_flow < 0:
            recommendations.append("Consider negotiating extended payment terms with suppliers")
            recommendations.append("Accelerate collections from customers with overdue receivables")
        if health_score and health_score.current_ratio < 1.0 if hasattr(health_score, 'current_ratio') else False:
            recommendations.append("Maintain higher cash reserves for operational stability")
        recommendations.append("Review recurring expenses for potential cost optimization")
        recommendations.append("Monitor cash flow weekly to identify trends early")
        
        return CashFlowNarrative(
            summary=summary.strip(),
            key_insights=insights,
            highlights=highlights,
            concerns=concerns,
            recommendations=recommendations
        )
    
    def generate_financial_advisory(
        self,
        db: Session,
        company_id: int,
        focus_areas: List[str] = None
    ) -> FinancialAdvisory:
        """Generate comprehensive financial advisory"""
        
        if focus_areas is None:
            focus_areas = ["cost_optimization", "cash_flow", "growth"]
        
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        latest_metrics = db.query(FinancialMetrics).filter(
            FinancialMetrics.company_id == company_id
        ).order_by(FinancialMetrics.created_at.desc()).first()
        
        latest_score = db.query(HealthScore).filter(
            HealthScore.company_id == company_id
        ).order_by(HealthScore.created_at.desc()).first()
        
        # Generate mock advisory
        return self._generate_mock_advisory(
            company_name=company.name,
            industry=company.industry.value if company.industry else "services",
            metrics=latest_metrics,
            health_score=latest_score,
            focus_areas=focus_areas
        )
    
    def _generate_mock_advisory(
        self,
        company_name: str,
        industry: str,
        metrics: Optional[FinancialMetrics],
        health_score: Optional[HealthScore],
        focus_areas: List[str]
    ) -> FinancialAdvisory:
        """Generate mock financial advisory"""
        
        recommendations = []
        potential_savings = 0.0
        
        # Cost Optimization Recommendations
        if "cost_optimization" in focus_areas:
            if metrics:
                # Mock analysis - in production would analyze actual expenses
                if metrics.net_margin and metrics.net_margin < 10:
                    recommendations.append({
                        "area": "cost_optimization",
                        "title": "Review Operational Expenses",
                        "description": "Analysis indicates potential for 5-10% cost reduction through vendor consolidation and process optimization.",
                        "impact": f"Potential annual savings: ₹{metrics.total_outflows * 0.05:,.0f}",
                        "priority": "high",
                        "actions": [
                            "Consolidate vendors for bulk discounts",
                            "Review utility contracts and negotiate rates",
                            "Implement energy efficiency measures",
                            "Audit recurring subscriptions"
                        ]
                    })
                    potential_savings += metrics.total_outflows * 0.05 if metrics.total_outflows else 50000
                
                if metrics.gross_margin and metrics.gross_margin < 60:
                    recommendations.append({
                        "area": "cost_optimization",
                        "title": "Improve Gross Margin",
                        "description": "Gross margin below industry average. Focus on pricing strategy and procurement efficiency.",
                        "impact": f"Potential margin improvement: {(70 - metrics.gross_margin)/2:.1f} percentage points",
                        "priority": "medium",
                        "actions": [
                            "Review pricing with cost-plus analysis",
                            "Negotiate better terms with key suppliers",
                            "Reduce waste in production process",
                            "Optimize inventory levels"
                        ]
                    })
            else:
                recommendations.append({
                    "area": "cost_optimization",
                    "title": "Upload Financial Data",
                    "description": "Upload bank statements or financial reports to receive personalized cost optimization recommendations.",
                    "impact": "Requires data analysis",
                    "priority": "high",
                    "actions": [
                        "Upload last 3 months bank statements",
                        "Add any accounting exports",
                        "Complete company profile"
                    ]
                })
        
        # Cash Flow Recommendations
        if "cash_flow" in focus_areas:
            if health_score:
                if health_score.cash_flow_score < 70:
                    recommendations.append({
                        "area": "cash_flow",
                        "title": "Improve Cash Flow Management",
                        "description": "Cash flow patterns suggest room for improvement in working capital management.",
                        "impact": "Improved liquidity and reduced financing costs",
                        "priority": "high",
                        "actions": [
                            "Implement invoice discounting for faster collection",
                            "Negotiate net-45 or net-60 payment terms with suppliers",
                            "Build cash reserve equivalent to 2 months expenses",
                            "Monitor cash flow weekly with automated alerts"
                        ]
                    })
                
                if health_score.dscr and health_score.dscr < 1.25:
                    recommendations.append({
                        "area": "cash_flow",
                        "title": "Strengthen Debt Service Coverage",
                        "description": "DSCR indicates potential strain on debt servicing capacity.",
                        "impact": "Better loan terms and reduced default risk",
                        "priority": "critical",
                        "actions": [
                            "Consider debt restructuring for extended terms",
                            "Accelerate collections to improve cash position",
                            "Explore equity infusion to reduce debt burden",
                            "Prioritize high-margin orders"
                        ]
                    })
            else:
                recommendations.append({
                    "area": "cash_flow",
                    "title": "Complete Financial Health Assessment",
                    "description": "Upload financial documents to get detailed cash flow analysis and recommendations.",
                    "impact": "Comprehensive cash flow insights",
                    "priority": "medium",
                    "actions": [
                        "Upload bank statements",
                        "Add GST returns if applicable",
                        "Complete financial profile"
                    ]
                })
        
        # Growth Recommendations
        if "growth" in focus_areas:
            if health_score and health_score.overall_score >= 60:
                recommendations.append({
                    "area": "growth",
                    "title": "Growth Financing Options",
                    "description": "Your financial health makes you eligible for various growth financing products.",
                    "impact": "Access to working capital for expansion",
                    "priority": "medium",
                    "actions": [
                        "Explore working capital loans for inventory financing",
                        "Consider invoice discounting for order execution",
                        "Evaluate equipment financing for capacity expansion",
                        "Review insurance coverage for business protection"
                    ]
                })
            elif health_score:
                recommendations.append({
                    "area": "growth",
                    "title": "Strengthen Foundation Before Scaling",
                    "description": "Focus on improving key metrics before aggressive growth expansion.",
                    "impact": "Sustainable growth trajectory",
                    "priority": "medium",
                    "actions": [
                        "Improve profit margins to 15%+",
                        "Build cash reserves before expansion",
                        "Reduce debt-to-equity ratio below 0.5",
                        "Establish robust financial controls"
                    ]
                })
        
        # Generate summary
        summary_parts = [
            f"Based on analysis of {company_name}'s financial data,",
        ]
        
        if health_score:
            if health_score.overall_score >= 70:
                summary_parts.append("your business shows strong financial health.")
            elif health_score.overall_score >= 50:
                summary_parts.append("there are opportunities to improve financial efficiency.")
            else:
                summary_parts.append("immediate attention to financial fundamentals is recommended.")
        
        summary = " ".join(summary_parts)
        
        if recommendations:
            summary += f"\n\nWe have identified {len(recommendations)} priority areas for improvement."
        
        # Growth opportunities
        growth_opportunities = [
            {
                "opportunity": "Working Capital Loan",
                "eligibility": "Available",
                "amount": "Up to ₹50L",
                "use_case": "Inventory, raw materials, or operational expenses"
            },
            {
                "opportunity": "Invoice Discounting",
                "eligibility": "Based on receivables",
                "amount": "Up to 80% of invoice value",
                "use_case": "Faster access to tied-up capital"
            },
            {
                "opportunity": "Equipment Financing",
                "eligibility": "Based on business vintage",
                "amount": "Up to ₹1Cr",
                "use_case": "Machinery, vehicles, or technology upgrade"
            }
        ]
        
        return FinancialAdvisory(
            summary=summary,
            recommendations=recommendations,
            potential_savings=round(potential_savings, 2),
            growth_opportunities=growth_opportunities
        )
    
    def generate_health_assessment_narrative(
        self,
        db: Session,
        company_id: int
    ) -> Dict[str, Any]:
        """Generate comprehensive health assessment narrative"""
        
        company = db.query(Company).filter(Company.id == company_id).first()
        health_score = db.query(HealthScore).filter(
            HealthScore.company_id == company_id
        ).order_by(HealthScore.created_at.desc()).first()
        
        if not health_score:
            return {
                "message": "No health assessment available. Please upload financial documents.",
                "next_steps": [
                    "Upload bank statements or financial exports",
                    "Complete company profile",
                    "Run health assessment"
                ]
            }
        
        # Generate mock narrative
        risk_level = health_score.risk_level.value
        overall_score = health_score.overall_score
        
        # Determine assessment tone
        if overall_score >= 80:
            tone = "excellent"
            emoji = "🏆"
        elif overall_score >= 60:
            tone = "healthy"
            emoji = "✅"
        elif overall_score >= 40:
            tone = "needs_work"
            emoji = "⚠️"
        else:
            tone = "critical"
            emoji = "🚨"
        
        narrative = f"""
{emoji} **{company.name if company else 'Your Company'} - Financial Health Assessment**

**Overall Score: {overall_score}/100** ({risk_level.upper()} Risk)

{emoji} **{tone.upper()}** - {'Outstanding financial performance with strong fundamentals.' if tone == 'excellent' else 'Generally healthy with some areas requiring attention.' if tone == 'healthy' else 'Several areas need improvement to strengthen financial position.' if tone == 'needs_work' else 'Immediate corrective action required to prevent financial distress.'}

---

### 📊 Score Breakdown

| Metric | Score | Status |
|--------|-------|--------|
| Cash Flow | {health_score.cash_flow_score}/100 | {'Excellent' if health_score.cash_flow_score >= 80 else 'Good' if health_score.cash_flow_score >= 60 else 'Fair' if health_score.cash_flow_score >= 40 else 'Needs Improvement'} |
| Profitability | {health_score.profitability_score}/100 | {'Excellent' if health_score.profitability_score >= 80 else 'Good' if health_score.profitability_score >= 60 else 'Fair' if health_score.profitability_score >= 40 else 'Needs Improvement'} |
| Leverage | {health_score.leverage_score}/100 | {'Excellent' if health_score.leverage_score >= 80 else 'Good' if health_score.leverage_score >= 60 else 'Fair' if health_score.leverage_score >= 40 else 'Needs Improvement'} |
| Efficiency | {health_score.efficiency_score}/100 | {'Excellent' if health_score.efficiency_score >= 80 else 'Good' if health_score.efficiency_score >= 60 else 'Fair' if health_score.efficiency_score >= 40 else 'Needs Improvement'} |
| Stability | {health_score.stability_score}/100 | {'Excellent' if health_score.stability_score >= 80 else 'Good' if health_score.stability_score >= 60 else 'Fair' if health_score.stability_score >= 40 else 'Needs Improvement'} |

---

### 💳 Credit Assessment

**Rating: {health_score.credit_rating}**

This rating is based on your financial health score and indicates {'very low credit risk' if health_score.credit_rating in ['AAA', 'AA'] else 'low credit risk' if health_score.credit_rating in ['A', 'BBB'] else 'moderate credit risk' if health_score.credit_rating in ['BB', 'B'] else 'high credit risk'}.

---

### 🎯 Key Focus Areas

{self._generate_focus_areas(health_score)}

---

### 📈 Next Steps

1. **Review this assessment** with your financial advisor
2. **Address any red flags** identified in the analysis
3. **Upload additional documents** for more accurate analysis
4. **Set up monitoring** to track improvements over time
"""
        
        return {
            "narrative": narrative.strip(),
            "overall_score": overall_score,
            "risk_level": risk_level,
            "credit_rating": health_score.credit_rating,
            "component_scores": {
                "cash_flow": health_score.cash_flow_score,
                "profitability": health_score.profitability_score,
                "leverage": health_score.leverage_score,
                "efficiency": health_score.efficiency_score,
                "stability": health_score.stability_score
            }
        }
    
    def _generate_focus_areas(self, health_score: HealthScore) -> str:
        """Generate key focus areas based on lowest scores"""
        scores = {
            "Cash Flow": health_score.cash_flow_score,
            "Profitability": health_score.profitability_score,
            "Leverage": health_score.leverage_score,
            "Efficiency": health_score.efficiency_score,
            "Stability": health_score.stability_score
        }
        
        # Sort by lowest score
        sorted_areas = sorted(scores.items(), key=lambda x: x[1])
        
        focus_lines = []
        for area, score in sorted_areas[:3]:  # Bottom 3 areas
            if score < 70:
                focus_lines.append(f"- **{area}**: Score of {score}/100 indicates room for improvement")
        
        if not focus_lines:
            return "- All key metrics are performing well. Maintain current practices!"
        
        return "\n".join(focus_lines)


# Global service instance
ai_narrative_service = AINarrativeService()

