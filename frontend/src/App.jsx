import { useState, useEffect } from 'react'
import Header from './components/Header'
import ItemsList from './components/ItemsList'
import './App.css'

const API_URL = 'http://localhost:5001/api'

function App() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch all items
  const fetchItems = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_URL}/items`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch items')
      }
      
      const data = await response.json()
      setItems(data)
    } catch (err) {
      console.error('Error fetching items:', err)
      setError('Failed to load items. Make sure the backend server is running on port 5000.')
    } finally {
      setLoading(false)
    }
  }

  // Fetch items on component mount
  useEffect(() => {
    fetchItems()
  }, [])

  return (
    <div className="app">
      <div className="container">
        <Header />
        <ItemsList 
          items={items} 
          loading={loading} 
          error={error}
        />
      </div>
    </div>
  )
}

export default App
