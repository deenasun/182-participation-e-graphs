import ItemCard from './ItemCard'

function ItemsList({ items, loading, error }) {
  if (loading) {
    return (
      <section className="items-list">
        <h2>Items</h2>
        <div className="items-container">
          <p className="loading">Loading items...</p>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="items-list">
        <h2>Items</h2>
        <div className="items-container">
          <p className="error">{error}</p>
        </div>
      </section>
    )
  }

  return (
    <section className="items-list">
      <h2>Items</h2>
      <div className="items-container">
        {items.length === 0 ? (
          <p className="loading">No items yet. Add one above!</p>
        ) : (
          items.map(item => (
            <ItemCard
              key={item.id}
              item={item}
            />
          ))
        )}
      </div>
    </section>
  )
}

export default ItemsList
