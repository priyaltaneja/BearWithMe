import React, { useState } from 'react'
import AddWordsModal from './AddWordsModal'
import ConfirmModal from './ConfirmModal'
import { Icons } from '../utils/icons'
import './WordLibrary.css'

function WordLibrary({ wordData, onWordClick, child, onAddWord, onDeleteWord }) {
  const [filter, setFilter] = useState('all')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState({ isOpen: false, wordText: null })

  const filters = [
    { id: 'all', label: 'All', count: wordData.length },
    { id: 'mastered', label: 'Mastered', count: wordData.filter(w => w.status === 'mastered').length },
    { id: 'in-progress', label: 'In Progress', count: wordData.filter(w => w.status === 'in-progress').length },
    { id: 'struggling', label: 'Struggling', count: wordData.filter(w => w.status === 'struggling').length },
    { id: 'not-started', label: 'Not Started', count: wordData.filter(w => w.status === 'not-started').length }
  ]

  const getFilteredWords = () => {
    if (filter === 'all') return wordData
    return wordData.filter(w => w.status === filter)
  }

  const filteredWords = getFilteredWords()

  const getStatusColor = (status) => {
    switch (status) {
      case 'mastered': return 'success'
      case 'in-progress': return 'terracotta'
      case 'struggling': return 'danger'
      case 'not-started': return 'muted'
      default: return 'muted'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'mastered': return '✓ Mastered'
      case 'in-progress': return 'In Progress'
      case 'struggling': return 'Struggling'
      case 'not-started': return 'Not Started'
      default: return status
    }
  }

  return (
    <div className="word-library">
      <div className="library-header">
        <div>
          <h2 className="library-title">Word Library</h2>
          <div className="library-stats">
            {wordData.length} total words
          </div>
        </div>
        <button 
          className="add-words-btn"
          onClick={() => setIsModalOpen(true)}
        >
          <Icons.Plus className="add-words-icon" />
          Add New Words
        </button>
      </div>

      <div className="filter-tabs">
        {filters.map(f => (
          <button
            key={f.id}
            className={`filter-tab ${filter === f.id ? 'active' : ''}`}
            onClick={() => setFilter(f.id)}
          >
            {f.label}
            <span className="filter-count">({f.count})</span>
          </button>
        ))}
      </div>

      <div className="word-cards-grid">
        {filteredWords.map((word, idx) => {
          const originalIndex = wordData.indexOf(word)
          return (
            <div
              key={idx}
              className={`word-card ${word.status} ${onWordClick ? 'clickable' : ''}`}
              onClick={() => onWordClick && onWordClick(originalIndex)}
            >
              <div className="word-card-header">
                <div className="word-card-name">{word.text}</div>
                <div className={`word-card-status ${getStatusColor(word.status)}`}>
                  {getStatusLabel(word.status)}
                </div>
              </div>

              <div className="word-card-body">
                <div className="word-card-metric">
                  <span className="metric-label">Practice Count:</span>
                  <span className="metric-value">{word.practiceCount || 0}</span>
                </div>

                {word.lastPracticed && (
                  <div className="word-card-metric">
                    <span className="metric-label">Last Practiced:</span>
                    <span className="metric-value">
                      {new Date(word.lastPracticed).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="word-card-footer">
                {onWordClick && (
                  <span className="view-details">View Details →</span>
                )}
                {onDeleteWord && (
                  <button
                    className="word-card-delete-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      setConfirmDelete({ isOpen: true, wordText: word.text })
                    }}
                    aria-label={`Delete ${word.text}`}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {filteredWords.length === 0 && (
        <div className="empty-library">
          <p>No words found in this category.</p>
        </div>
      )}

      {/* Add Words Modal */}
      <AddWordsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAddWord={onAddWord}
        onDeleteWord={onDeleteWord}
        wordData={wordData}
        child={child}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={confirmDelete.isOpen}
        onClose={() => setConfirmDelete({ isOpen: false, wordText: null })}
        onConfirm={() => {
          if (confirmDelete.wordText && onDeleteWord) {
            onDeleteWord(confirmDelete.wordText)
          }
        }}
        title="Delete Word"
        message={`Are you sure you want to delete "${confirmDelete.wordText}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
      />
    </div>
  )
}

export default WordLibrary

