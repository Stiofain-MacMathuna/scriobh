import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import NoteEditor from './NoteEditor';

const API_URL = import.meta.env.VITE_API_URL;

export default function DashboardLayout() {
  const [openNotes, setOpenNotes] = useState([]);
  const [activeNoteId, setActiveNoteId] = useState(null);
  const [isMarkdownMode, setIsMarkdownMode] = useState(true);

  const activeNote = openNotes.find((note) => note.id === activeNoteId);

  async function fetchNotes() {
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('No token found. Cannot fetch notes.');
      return;
    }

    try {
      const res = await fetch(`${API_URL}/notes`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        console.error('Failed to fetch notes:', await res.json());
        return;
      }

      const data = await res.json();
      setOpenNotes(data);

      if (!data.some((note) => note.id === activeNoteId)) {
        setActiveNoteId(data.length > 0 ? data[0].id : null);
      }
    } catch (err) {
      console.error('Error fetching notes:', err);
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
          {activeNote ? (
            <NoteEditor
              note={activeNote}
              onChange={updateNoteContent}
              onDelete={handleDeleteNote}
              
              isMarkdownMode={isMarkdownMode}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-300">
              Select a note to begin editing
            </div>
          )}
        </div>
      </div>
    </div>
  );
}