import { useState } from 'react'
import './App.css'

// FileUpload component for handling PDF uploads
const FileUpload = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileChange = (event) => {
    setFile(event.target.files[0])
    setError(null)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    
    if (!file) {
      setError('Please select a file')
      return
    }
    
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file')
      return
    }
    
    const formData = new FormData()
    formData.append('file', file)
    
    setLoading(true)
    setError(null)
    
    try {
      // Connect to your Flask backend
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to analyze file')
      }
      
      const data = await response.json()
      onUploadComplete(data.results)
    } catch (err) {
      setError('Error processing file: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="file-upload">
      <h2>Upload Malaria Test PDF</h2>
      <form onSubmit={handleSubmit}>
        <input 
          type="file" 
          accept="application/pdf"
          onChange={handleFileChange}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Analyze'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
    </div>
  )
}

// Results display component
const ResultsDisplay = ({ results }) => {
  if (!results) return null
  
  return (
    <div className="results">
      <h3>Analysis Results</h3>
      
      <div className="result-item">
        <strong>Diagnosis:</strong> 
        <span className={results.diagnosis === 'Positive' ? 'positive' : 'negative'}>
          {results.diagnosis}
        </span>
      </div>
      
      {results.diagnosis === 'Positive' && (
        <>
          <div className="result-item">
            <strong>Parasites Detected:</strong> 
            {results.parasites_detected && results.parasites_detected.length > 0 
              ? results.parasites_detected.join(', ') 
              : 'Unknown parasite type'}
          </div>
          
          <div className="result-item">
            <strong>Parasite Count:</strong> 
            {results.parasite_count}
          </div>
        </>
      )}
      
      <div className="result-item">
        <strong>Confidence:</strong> 
        {(results.confidence * 100).toFixed(2)}%
      </div>
      
      <div className="result-item">
        <strong>Images Analyzed:</strong> 
        {results.images_analyzed}
      </div>
      
      <div className="result-summary">
        <p>
          <strong>Summary: </strong> 
          {results.diagnosis === 'Positive' 
            ? `Malaria infection detected with ${(results.confidence * 100).toFixed(2)}% confidence.` 
            : results.diagnosis === 'Negative'
              ? 'No malaria infection detected in the provided sample.'
              : 'Analysis was inconclusive. Please try again with a clearer image.'}
        </p>
      </div>
    </div>
  )
}

// Main App component
function App() {
  const [results, setResults] = useState(null)

  const handleUploadComplete = (analysisResults) => {
    setResults(analysisResults)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Malaria Analysis Tool</h1>
        <p>Upload malaria test PDFs for automated analysis</p>
      </header>
      
      <main>
        <FileUpload onUploadComplete={handleUploadComplete} />
        {results && <ResultsDisplay results={results} />}
      </main>
      
      <footer>
        <p>© 2025 Malaria Analysis Tool - CS Student Project</p>
      </footer>
    </div>
  )
}

export default App
