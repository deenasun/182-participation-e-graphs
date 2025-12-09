import React from 'react'

function ItemCard({ item }) {
  return (
    <div className="item-card">
      <div className="item-header">
        <span className="item-name">{item.name}</span>
        <span className="item-id">ID: {item.id}</span>
      </div>
      <p className="item-description">{item.description}</p>
    </div>
  )
}

export default ItemCard
