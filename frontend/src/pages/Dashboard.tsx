import { TrendingUp, TrendingDown, DollarSign, AlertTriangle, CheckCircle, FileText } from 'lucide-react'
import { useAuth } from '../App'
import { Link } from 'react-router-dom'

const Dashboard = () => {
  const { user } = useAuth()
  
  // Mock data for demo
  const stats = [
    { label: 'Overall Health Score', value: '72.5', change: '+5.2%', trend: 'up', icon: CheckCircle, color: 'success' },
    { label: 'Monthly Revenue', value: '₹15L', change: '+12.3%', trend: 'up', icon: DollarSign, color: 'primary' },
    { label: 'Net Cash Flow', value: '₹2.5L', change: '-2.1%', trend: 'down', icon: TrendingUp, color: 'warning' },
    { label: 'Anomalies', value: '3', change: '2 critical', trend: 'neutral', icon: AlertTriangle, color: 'danger' },
  ]
  
  const recentDocuments = [
    { name: 'ICICI Bank Statement - Q3 2024', type: 'bank_statement', status: 'completed', date: '2024-01-15' },
    { name: 'Tally Export - December 2024', type: 'tally_export', status: 'completed', date: '2024-01-10' },
    { name: 'GST Return - December 2024', type: 'gst_return', status: 'processing', date: '2024-01-08' },
  ]
  
  const scoreBreakdown = [
    { label: 'Cash Flow', score: 78, color: 'bg-success-500' },
    { label: 'Profitability', score: 68, color: 'bg-primary-500' },
    { label: 'Leverage', score: 75, color: 'bg-primary-500' },
    { label: 'Efficiency', score: 70, color: 'bg-warning-500' },
    { label: 'Stability', score: 65, color: 'bg-warning-500' },
  ]
  
  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome back, {user?.full_name || 'User'}</p>
        </div>
        <div className="mt-4 md:mt-0">
          <Link to="/documents" className="btn-primary">
            <FileText className="w-4 h-4 mr-2" />
            Upload Documents
          </Link>
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="card p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`p-2 rounded-lg ${
                stat.color === 'success' ? 'bg-success-100 text-success-600' :
                stat.color === 'primary' ? 'bg-primary-100 text-primary-600' :
                stat.color === 'warning' ? 'bg-warning-100 text-warning-600' :
                'bg-danger-100 text-danger-600'
              }`}>
                <stat.icon className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-center mt-3">
              {stat.trend === 'up' && <TrendingUp className="w-4 h-4 text-success-500 mr-1" />}
              {stat.trend === 'down' && <TrendingDown className="w-4 h-4 text-danger-500 mr-1" />}
              <span className={`text-sm ${
                stat.trend === 'up' ? 'text-success-600' :
                stat.trend === 'down' ? 'text-danger-600' :
                'text-gray-500'
              }`}>
                {stat.change}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Health Score Card */}
        <div className="card lg:col-span-2">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">Financial Health Score</h2>
          </div>
          <div className="card-body">
            <div className="flex flex-col md:flex-row items-center gap-8">
              {/* Score Circle */}
              <div className="relative">
                <div className="w-40 h-40 rounded-full bg-success-500 flex items-center justify-center text-white text-4xl font-bold">
                  72.5
                </div>
                <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-success-100 text-success-700 px-3 py-1 rounded-full text-sm font-medium">
                  Low Risk
                </div>
              </div>
              
              {/* Score Breakdown */}
              <div className="flex-1 w-full">
                <div className="space-y-4">
                  {scoreBreakdown.map((item) => (
                    <div key={item.label}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">{item.label}</span>
                        <span className="text-sm text-gray-500">{item.score}/100</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${item.color}`}
                          style={{ width: `${item.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-gray-100">
              <Link to="/health-score" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                View detailed analysis →
              </Link>
            </div>
          </div>
        </div>
        
        {/* Recent Documents */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Recent Documents</h2>
            <Link to="/documents" className="text-sm text-primary-600 hover:text-primary-700">View all</Link>
          </div>
          <div className="divide-y divide-gray-100">
            {recentDocuments.map((doc, index) => (
              <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${
                    doc.status === 'completed' ? 'bg-success-100' : 'bg-warning-100'
                  }`}>
                    <FileText className={`w-4 h-4 ${
                      doc.status === 'completed' ? 'text-success-600' : 'text-warning-600'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{doc.name}</p>
                    <p className="text-xs text-gray-500">{doc.date}</p>
                  </div>
                  <span className={`badge ${
                    doc.status === 'completed' ? 'badge-success' : 'badge-warning'
                  }`}>
                    {doc.status}
                  </span>
                </div>
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { title: 'Improve Cash Flow', description: 'Consider accelerating collections to improve cash position', priority: 'high' },
              { title: 'Cost Optimization', description: 'Review recurring expenses for potential savings of ₹50K/month', priority: 'medium' },
              { title: 'Debt Restructuring', description: 'Explore better loan terms given improved credit profile', priority: 'low' },
            ].map((rec, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{rec.title}</h3>
                  <span className={`badge ${
                    rec.priority === 'high' ? 'badge-danger' :
                    rec.priority === 'medium' ? 'badge-warning' : 'badge-primary'
                  }`}>
                    {rec.priority}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{rec.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

