import { useState } from 'react'

function AddItemForm({ onAddItem }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!name.trim() || !description.trim()) {
      return
    }
    
    setIsSubmitting(true)
    const success = await onAddItem(name.trim(), description.trim())
    
    if (success) {
      setName('')
      setDescription('')
    }
    
    setIsSubmitting(false)
  }

  return (
    <section className="add-item">
      <h2>Add New Item</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Item name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          disabled={isSubmitting}
        />
        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          disabled={isSubmitting}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Adding...' : 'Add Item'}
        </button>
      </form>
    </section>
  )
}

export default AddItemForm
