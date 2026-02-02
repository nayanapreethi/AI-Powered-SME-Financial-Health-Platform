import { CheckCircle, AlertTriangle, TrendingUp, Lightbulb, Shield } from 'lucide-react'

const HealthScore = () => {
  const score = 72.5
  const riskLevel = 'low'
  const creditRating = 'BBB'
  
  const scoreComponents = [
    { label: 'Cash Flow', score: 78, weight: 25 },
    { label: 'Profitability', score: 68, weight: 25 },
    { label: 'Leverage', score: 75, weight: 20 },
    { label: 'Efficiency', score: 70, weight: 15 },
    { label: 'Stability', score: 65, weight: 15 },
  ]
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'primary'
    if (score >= 40) return 'warning'
    return 'danger'
  }
  
  return (
    <div className="space-y-6 animate-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Health Score</h1>
          <p className="text-gray-500 mt-1">Your comprehensive financial health assessment</p>
        </div>
        <button className="btn-primary mt-4 md:mt-0">
          Run New Analysis
        </button>
      </div>
      
      {/* Main Score Card */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col md:flex-row items-center gap-8">
            {/* Score Circle */}
            <div className="relative">
              <div className={`w-48 h-48 rounded-full flex items-center justify-center text-white text-5xl font-bold ${
                score >= 80 ? 'bg-success-500' :
                score >= 60 ? 'bg-primary-500' :
                score >= 40 ? 'bg-warning-500' : 'bg-danger-500'
              }`}>
                {score}
              </div>
              <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-white px-4 py-1 rounded-full shadow-md">
                <span className={`badge ${
                  riskLevel === 'low' ? 'badge-success' :
                  riskLevel === 'medium' ? 'badge-warning' : 'badge-danger'
                }`}>
                  {riskLevel.toUpperCase()} RISK
                </span>
              </div>
            </div>
            
            {/* Score Info */}
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Financial Health Score</h2>
              <p className="text-gray-600 mb-4">
                Your business demonstrates healthy financial performance with strong cash flow generation.
                Profitability metrics are above industry average.
              </p>
              <div className="flex items-center justify-center md:justify-start space-x-4">
                <div className="flex items-center">
                  <Shield className="w-5 h-5 text-success-500 mr-2" />
                  <span className="text-sm text-gray-600">Credit Rating: <strong>{creditRating}</strong></span>
                </div>
                <div className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-success-500 mr-2" />
                  <span className="text-sm text-gray-600">Trend: <strong>Improving</strong></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Component Scores */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Score Breakdown</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scoreComponents.map((component) => (
              <div key={component.label} className="p-4 bg-gray-50 rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium text-gray-900">{component.label}</span>
                  <span className={`badge ${
                    getScoreColor(component.score) === 'success' ? 'badge-success' :
                    getScoreColor(component.score) === 'primary' ? 'badge-primary' :
                    getScoreColor(component.score) === 'warning' ? 'badge-warning' : 'badge-danger'
                  }`}>
                    {component.score}/100
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      getScoreColor(component.score) === 'success' ? 'bg-success-500' :
                      getScoreColor(component.score) === 'primary' ? 'bg-primary-500' :
                      getScoreColor(component.score) === 'warning' ? 'bg-warning-500' : 'bg-danger-500'
                    }`}
                    style={{ width: `${component.score}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2">Weight: {component.weight}%</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Recommendations */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">AI Recommendations</h2>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {[
              { icon: CheckCircle, title: 'Strong Cash Position', description: 'Maintain current cash reserves for operational stability', color: 'success' },
              { icon: Lightbulb, title: 'Optimize Working Capital', description: 'Consider invoice discounting for faster collections', color: 'primary' },
              { icon: AlertTriangle, title: 'Monitor Expense Growth', description: 'Review marketing spend efficiency in Q4', color: 'warning' },
            ].map((rec, index) => (
              <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className={`p-2 rounded-lg ${
                  rec.color === 'success' ? 'bg-success-100' :
                  rec.color === 'primary' ? 'bg-primary-100' : 'bg-warning-100'
                }`}>
                  <rec.icon className={`w-5 h-5 ${
                    rec.color === 'success' ? 'text-success-600' :
                    rec.color === 'primary' ? 'text-primary-600' : 'text-warning-600'
                  }`} />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{rec.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default HealthScore

