import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import NoteEditor from './NoteEditor';

const API_URL = import.meta.env.VITE_API_URL;

function fetchWithTimeout(url, options = {}, timeout = 10000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  return fetch(url, { ...options, signal: controller.signal }).finally(() => clearTimeout(id));
}

export default function DashboardLayout() {
  const [openNotes, setOpenNotes] = useState([]);
  const [activeNoteId, setActiveNoteId] = useState(null);
  const [isMarkdownMode, setIsMarkdownMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const activeNote = openNotes.find((note) => note.id === activeNoteId);

  async function fetchNotes() {
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('No token found. Cannot fetch notes.');
      setError('Authentication required.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetchWithTimeout(`${API_URL}/notes/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // Handle 404 specifically
      if (res.status === 404) {
        console.log("No notes found for this user. Displaying a blank slate.");
        setOpenNotes([]);
        setActiveNoteId(null);
        return;
      }

      if (!res.ok) {
        let errData = {};
        try {
          errData = await res.json();
        } catch {}
        console.error('Failed to fetch notes:', errData);
        setError('Failed to load notes.');
        return;
      }

      const data = await res.json();
      setOpenNotes(data);

      if (data.length > 0 && !data.some((note) => note.id === activeNoteId)) {
        setActiveNoteId(data[0].id);
      }
    } catch (err) {
      console.error('Error fetching notes:', err);
      setError('Network error while loading notes.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchNotes();
  }, []);

  function handleSelectNote(note) {
    if (!openNotes.some((n) => n.id === note.id)) {
      setOpenNotes([...openNotes, note]);
    }
    setActiveNoteId(note.id);
  }

  function handleCreateNote(newNote) {
    setOpenNotes((prev) => [...prev, newNote]);
    setActiveNoteId(newNote.id);
  }

  function updateNoteContent(updatedNote) {
    setOpenNotes((notes) =>
      notes.map((note) =>
        note.id === updatedNote.id ? updatedNote : note
      )
    );
  }

  function handleDeleteNote(id) {
    setOpenNotes((notes) => notes.filter((note) => note.id !== id));
    if (activeNoteId === id) {
      setActiveNoteId(null);
    }
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-[rgb(15,23,42)]">
      <div className="flex flex-1 p-3 gap-3 overflow-hidden">
        <div className="w-56 shrink-0 bg-[#0f172a] overflow-hidden flex flex-col">
          <Sidebar
            notes={openNotes}
            activeNoteId={activeNoteId}
            onSelect={handleSelectNote}
            onCreate={handleCreateNote}
            onDelete={handleDeleteNote}
            isMarkdownMode={isMarkdownMode}
            setIsMarkdownMode={setIsMarkdownMode}
          />
        </div>

        <div className="flex-1 rounded-2xl bg-[#1e293b] shadow-2xl backdrop-blur-md overflow-hidden flex flex-col p-6">
          {loading && (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              Loading notes...
            </div>
          )}
          {error && (
            <div className="flex-1 flex items-center justify-center text-red-500">
              {error}
            </div>
          )}
          {!loading && !error && activeNote ? (
            <NoteEditor
              note={activeNote}
              onChange={updateNoteContent}
              onDelete={handleDeleteNote}
              isMarkdownMode={isMarkdownMode}
            />
          ) : (
            !loading &&
            !error && (
              <div className="flex-1 flex items-center justify-center text-gray-300">
                Select a note or create a new one to begin editing
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}