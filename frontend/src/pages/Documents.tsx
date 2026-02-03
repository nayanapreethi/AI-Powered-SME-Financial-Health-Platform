import { useState, useCallback } from 'react'
import { Upload, FileText, X, CheckCircle, Clock, AlertCircle, File as FileIcon } from 'lucide-react'

const Documents = () => {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  
  const documents = [
    { id: 1, name: 'ICICI Bank Statement - Q4 2024.pdf', type: 'bank_statement', status: 'completed', size: '2.4 MB', date: '2024-01-15' },
    { id: 2, name: 'Tally Export - December 2024.xlsx', type: 'tally_export', status: 'completed', size: '1.1 MB', date: '2024-01-10' },
    { id: 3, name: 'GST Return GSTR-3B - Dec 2024.pdf', type: 'gst_return', status: 'processing', size: '856 KB', date: '2024-01-08' },
    { id: 4, name: 'HDFC Bank Statement - Nov 2024.pdf', type: 'bank_statement', status: 'completed', size: '2.1 MB', date: '2024-01-05' },
  ]
  
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFiles = Array.from(e.dataTransfer.files)
      setFiles(prev => [...prev, ...newFiles])
    }
  }, [])
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files)
      setFiles(prev => [...prev, ...newFiles])
    }
  }
  
  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }
  
  const uploadFiles = async () => {
    setUploading(true)
    // Simulate upload
    setTimeout(() => {
      setUploading(false)
      setFiles([])
    }, 2000)
  }
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-500" />
      case 'processing':
        return <Clock className="w-5 h-5 text-warning-500" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-danger-500" />
      default:
        return <FileIcon className="w-5 h-5 text-gray-400" />
    }
  }
  
  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-500 mt-1">Upload and manage your financial documents</p>
        </div>
      </div>
      
      {/* Upload Area */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Upload Documents</h2>
        </div>
        <div className="card-body">
          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              dragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-300 hover:border-primary-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Drag and drop your files here
            </p>
            <p className="text-gray-500 mb-4">
              or click to browse from your computer
            </p>
            <p className="text-sm text-gray-400">
              Supported formats: PDF, CSV, XLSX (Max 50MB)
            </p>
            <input
              type="file"
              multiple
              accept=".pdf,.csv,.xlsx,.xls"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="btn-primary mt-4 inline-block cursor-pointer">
              Select Files
            </label>
          </div>
          
          {/* Selected Files */}
          {files.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-sm font-medium text-gray-700">{files.length} file(s) selected</p>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 hover:bg-gray-200 rounded"
                    >
                      <X className="w-4 h-4 text-gray-500" />
                    </button>
                  </div>
                ))}
              </div>
              <button
                onClick={uploadFiles}
                disabled={uploading}
                className="btn-primary"
              >
                {uploading ? 'Uploading...' : 'Upload Files'}
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Document List */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Your Documents</h2>
        </div>
        <div className="divide-y divide-gray-100">
          {documents.map((doc) => (
            <div key={doc.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-primary-100 rounded-lg">
                  {getStatusIcon(doc.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{doc.name}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-500">{doc.size}</span>
                    <span className="text-gray-300">•</span>
                    <span className="text-xs text-gray-500">{doc.date}</span>
                    <span className="text-gray-300">•</span>
                    <span className={`badge ${
                      doc.status === 'completed' ? 'badge-success' :
                      doc.status === 'processing' ? 'badge-warning' : 'badge-danger'
                    }`}>
                      {doc.status}
                    </span>
                  </div>
                </div>
                <button className="btn-secondary text-sm">
                  View
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Documents

