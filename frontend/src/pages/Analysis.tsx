import { TrendingUp, TrendingDown, DollarSign, Percent, Activity } from 'lucide-react'

const Analysis = () => {
  const metrics = [
    { label: 'Current Ratio', value: '1.45', benchmark: '1.2-2.0', status: 'good', icon: Activity },
    { label: 'DSCR', value: '1.85', benchmark: '>1.25', status: 'good', icon: DollarSign },
    { label: 'Net Margin', value: '12.5%', benchmark: '8-15%', status: 'good', icon: Percent },
    { label: 'Debt to Equity', value: '0.45', benchmark: '<0.6', status: 'good', icon: TrendingDown },
  ]
  
  const cashFlowData = [
    { month: 'Aug', inflow: 45, outflow: 38 },
    { month: 'Sep', inflow: 52, outflow: 42 },
    { month: 'Oct', inflow: 48, outflow: 45 },
    { month: 'Nov', inflow: 55, outflow: 44 },
    { month: 'Dec', inflow: 62, outflow: 50 },
    { month: 'Jan', inflow: 58, outflow: 48 },
  ]
  
  return (
    <div className="space-y-6 animate-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Analysis</h1>
          <p className="text-gray-500 mt-1">Detailed financial metrics and performance indicators</p>
        </div>
        <button className="btn-primary mt-4 md:mt-0">
          Generate Report
        </button>
      </div>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <div className={`p-2 rounded-lg ${
                metric.status === 'good' ? 'bg-success-100 text-success-600' :
                metric.status === 'warning' ? 'bg-warning-100 text-warning-600' :
                'bg-danger-100 text-danger-600'
              }`}>
                <metric.icon className="w-5 h-5" />
              </div>
              <span className={`badge ${
                metric.status === 'good' ? 'badge-success' :
                metric.status === 'warning' ? 'badge-warning' : 'badge-danger'
              }`}>
                {metric.status}
              </span>
            </div>
            <p className="text-sm text-gray-500">{metric.label}</p>
            <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
            <p className="text-xs text-gray-400 mt-1">Benchmark: {metric.benchmark}</p>
          </div>
        ))}
      </div>
      
      {/* Cash Flow Chart */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Cash Flow Trend</h2>
        </div>
        <div className="card-body">
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500">Cash flow visualization</p>
              <p className="text-sm text-gray-400 mt-1">Install recharts to see chart</p>
            </div>
          </div>
          <div className="flex items-center justify-center space-x-6 mt-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-success-500 rounded-full mr-2" />
              <span className="text-sm text-gray-600">Inflows</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-danger-500 rounded-full mr-2" />
              <span className="text-sm text-gray-600">Outflows</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Detailed Ratios */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Detailed Ratio Analysis</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Ratio</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Current</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Benchmark</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {metrics.map((metric) => (
                <tr key={metric.label} className="hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm font-medium text-gray-900">{metric.label}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{metric.value}</td>
                  <td className="py-3 px-4 text-sm text-gray-500">{metric.benchmark}</td>
                  <td className="py-3 px-4">
                    <span className={`badge ${
                      metric.status === 'good' ? 'badge-success' :
                      metric.status === 'warning' ? 'badge-warning' : 'badge-danger'
                    }`}>
                      {metric.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Analysis

