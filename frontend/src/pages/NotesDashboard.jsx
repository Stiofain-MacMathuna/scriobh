import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import _ from 'lodash';
import { fetchWithAuth } from '../utils/fetchWithAuth';

const API_URL = import.meta.env.VITE_API_URL;

function NotesDashboard() {
  const [notes, setNotes] = useState([]);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchNotes = useCallback(async (currentSearchTerm) => {
    setLoading(true);
    setError('');
    try {
      const url = currentSearchTerm
        ? `${API_URL}/notes/?search=${encodeURIComponent(currentSearchTerm)}`
        : `${API_URL}/notes/`;

      const res = await fetchWithAuth(url, {}, navigate);
      if (!res) return;

      const data = await res.json();
      if (!Array.isArray(data)) throw new Error('Invalid notes format');
      setNotes(data);
    } catch (err) {
      setError('Error loading notes.');
      console.error('Error fetching notes:', err);
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const debouncedSearch = useCallback(
    _.debounce((term) => {
      fetchNotes(term);
    }, 500),
    [fetchNotes]
  );

  useEffect(() => {
    debouncedSearch(searchTerm);
    return () => {
      debouncedSearch.cancel();
    };
  }, [searchTerm, debouncedSearch]);

  const handleAddNote = async () => {
    try {
      const res = await fetchWithAuth(`${API_URL}/notes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, content: newContent }),
      }, navigate);
      if (!res) return;

      const created = await res.json();
      setNotes((prev) => [...prev, created]);
      setNewTitle('');
      setNewContent('');
      setSearchTerm('');
    } catch (err) {
      setError('Error adding note.');
      console.error('Error adding note:', err);
    }
  };

  const handleDeleteNote = async (id) => {
    try {
      const res = await fetchWithAuth(`${API_URL}/notes/${id}/`, {
        method: 'DELETE',
      }, navigate);
      if (!res) return;

      setNotes((prev) => prev.filter((note) => note.id !== id));
    } catch (err) {
      setError('Error deleting note.');
      console.error('Error deleting note:', err);
    }
  };

  const handleEditNote = (note) => {
    setEditingNoteId(note.id);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const handleUpdateNote = async () => {
    try {
      const res = await fetchWithAuth(`${API_URL}/notes/${editingNoteId}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: editTitle, content: editContent }),
      }, navigate);
      if (!res) return;

      const updated = await res.json();
      setNotes((prev) =>
        prev.map((note) => (note.id === updated.id ? updated : note))
      );
      setEditingNoteId(null);
      setEditTitle('');
      setEditContent('');
    } catch (err) {
      setError('Error updating note.');
      console.error('Error updating note:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setSearchTerm('');
    navigate('/');
  };

  if (loading) {
    return <p>Loading notes...</p>;
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Your Notes</h2>
      <button onClick={handleLogout}>Logout</button>

      <input
        type="text"
        placeholder="Search notes"
        value={searchTerm}
        onChange={handleSearchChange}
        style={{ marginTop: '1rem', marginBottom: '1rem', display: 'block' }}
      />

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={{ marginTop: '1rem' }}>
        <input
          type="text"
          placeholder="Title"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          style={{ marginBottom: '0.5rem', display: 'block' }}
        />
        <input
          type="text"
          placeholder="Content (Markdown supported)"
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          style={{ marginBottom: '0.5rem', display: 'block' }}
        />
        <button onClick={handleAddNote} disabled={!newTitle || !newContent}>
          Add
        </button>
      </div>

      <ul key={searchTerm} style={{ marginTop: '2rem' }}>
        {notes.map((note) => (
          <li key={note.id} style={{ marginBottom: '1rem' }}>
            {editingNoteId === note.id ? (
              <>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Edit title"
                />
                <input
                  type="text"
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  placeholder="Edit content"
                />
                <button onClick={handleUpdateNote}>Save</button>
                <button onClick={() => setEditingNoteId(null)}>Cancel</button>
              </>
            ) : (
              <>
                <strong>{note.title}</strong>
                <div style={{ marginTop: '0.5rem' }}>
                  <ReactMarkdown>{note.content}</ReactMarkdown>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#666' }}>
                  Created: {new Date(note.created_at).toLocaleString()}<br />
                  Updated: {new Date(note.updated_at).toLocaleString()}
                </div>
                <button onClick={() => handleEditNote(note)} style={{ marginLeft: '1rem' }}>
                  Edit
                </button>
                <button onClick={() => handleDeleteNote(note.id)} style={{ marginLeft: '0.5rem' }}>
                  Delete
                </button>
              </>
            )}
          </li>
        ))}
      </ul>
      {!loading && !error && notes.length === 0 && (
        <p>No notes found.</p>
      )}
    </div>
  );
}

export default NotesDashboard;