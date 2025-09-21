import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const API_URL = import.meta.env.VITE_API_URL;

function fetchWithTimeout(url, options = {}, timeout = 10000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  return fetch(url, { ...options, signal: controller.signal }).finally(() => clearTimeout(id));
}

function NotesDashboard() {
  const [notes, setNotes] = useState([]);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      navigate('/');
      return;
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload.exp * 1000 < Date.now()) {
        localStorage.removeItem('token');
        navigate('/');
      }
    } catch {
      localStorage.removeItem('token');
      navigate('/');
    }
  }, []);

  useEffect(() => {
    const delay = setTimeout(() => {
      const fetchNotes = async () => {
        setLoading(true);
        setError('');
        try {
          const url = searchTerm
            ? `${API_URL}/notes?search=${encodeURIComponent(searchTerm)}`
            : `${API_URL}/notes`;

          const res = await fetchWithTimeout(url, {
            headers: { Authorization: `Bearer ${token}` },
          });

          if (!res.ok) throw new Error('Failed to fetch notes');
          const data = await res.json();
          setNotes(data);
        } catch (err) {
          setError('Error loading notes.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };

      fetchNotes();
    }, 500);

    return () => clearTimeout(delay);
  }, [searchTerm]);

  const handleAddNote = async () => {
    try {
      const res = await fetchWithTimeout(`${API_URL}/notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: newTitle, content: newContent }),
      });

      if (!res.ok) throw new Error('Failed to add note');
      const created = await res.json();
      setNotes((prev) => [...prev, created]);
      setNewTitle('');
      setNewContent('');
      setSearchTerm('');
    } catch (err) {
      setError('Error adding note.');
      console.error(err);
    }
  };

  const handleDeleteNote = async (id) => {
    try {
      const res = await fetchWithTimeout(`${API_URL}/notes/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error('Failed to delete note');
      setNotes((prev) => prev.filter((note) => note.id !== id));
    } catch (err) {
      setError('Error deleting note.');
      console.error(err);
    }
  };

  const handleEditNote = (note) => {
    setEditingNoteId(note.id);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const handleUpdateNote = async () => {
    try {
      const res = await fetchWithTimeout(`${API_URL}/notes/${editingNoteId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: editTitle, content: editContent }),
      });

      if (!res.ok) throw new Error('Failed to update note');
      const updated = await res.json();
      setNotes((prev) =>
        prev.map((note) => (note.id === updated.id ? updated : note))
      );
      setEditingNoteId(null);
      setEditTitle('');
      setEditContent('');
    } catch (err) {
      setError('Error updating note.');
      console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setSearchTerm('');
    navigate('/');
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Your Notes</h2>
      <button onClick={handleLogout}>Logout</button>

      <input
        type="text"
        placeholder="Search notes"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{ marginTop: '1rem', marginBottom: '1rem', display: 'block' }}
      />

      {loading && <p>Loading notes...</p>}
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
    </div>
  );
}

export default NotesDashboard;