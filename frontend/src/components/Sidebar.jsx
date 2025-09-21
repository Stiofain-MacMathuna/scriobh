import { useNavigate } from 'react-router-dom';
import '../styles/scrollbar.css';
import Tooltip from './Tooltip';

export default function Sidebar({ notes, activeNoteId, onSelect, onCreate, onDelete, isMarkdownMode, setIsMarkdownMode }) {
  const navigate = useNavigate();

  const handleCreate = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('No token found. Redirecting to login...');
      navigate('/login');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: 'Untitled Note',
          content: '',
        }),
      });

      if (res.status === 401) {
        console.warn('Unauthorized. Redirecting to login...');
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }

      if (!res.ok) {
        const errData = await res.json();
        console.warn('Create failed:', errData);
        return;
      }

      const newNote = await res.json();
      onCreate(newNote);
      onSelect(newNote);
    } catch (err) {
      console.error('Failed to create note:', err);
    }
  };

  const handleDelete = async (e, noteId) => {
    e.stopPropagation();
    const confirmed = window.confirm('Are you sure you want to delete this note?');
    if (!confirmed) return;

    try {
      const res = await fetch(`http://localhost:8000/notes/${noteId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!res.ok) {
        const errorBody = await res.json().catch(() => ({}));
        console.error('Delete failed:', errorBody);
        if (res.status === 404) {
          alert('Note not found or already deleted.');
        }
        return;
      }

      onDelete(noteId);
    } catch (err) {
      console.error('Error deleting note:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleToggleMarkdown = () => {
    setIsMarkdownMode(!isMarkdownMode);
  };

  const MarkdownIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className="h-7 w-7"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14 9l-4 4-4-4" />
      <path d="M12 21V3" />
    </svg>
  );

  return (
    <div className="h-full w-full flex flex-col p-4 text-white">
      {/* Logo Section */}
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-[#34D399]">scríobh</h1>
      </div>

      {/* Scrollable list of notes */}
      <div className="flex-1 overflow-y-auto mb-4 custom-scrollbar">
        {Array.isArray(notes) && notes.length > 0 ? (
          notes.map((note) => (
            <button
              key={note.id}
              onClick={() => onSelect(note)}
              className={`group flex items-center min-w-0 w-full text-left py-2 mb-2 rounded transition-colors bg-transparent focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                activeNoteId === note.id ? 'text-[#34D399]' : 'text-white hover:text-gray-400'
              }`}
            >
              <span className="truncate whitespace-nowrap overflow-hidden text-lg">
                {note.title || 'Untitled'}
              </span>
              <button
                onClick={(e) => handleDelete(e, note.id)}
                className="ml-auto invisible group-hover:visible text-red-400 hover:text-red-500"
                aria-label={`Delete ${note.title || 'Untitled'} note`}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.013 21H7.987a2 2 0 01-1.92-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </button>
          ))
        ) : (
          <div className="text-gray-400">No notes found.</div>
        )}
      </div>

      {/* Buttons at the bottom */}
      <div className="shrink-0 flex items-center justify-between">
        <Tooltip text="Log Out">
          <button
            onClick={handleLogout}
            className="p-2 rounded-full text-white transition hover:bg-white/20"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-7 w-7"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
          </button>
        </Tooltip>

        <Tooltip text={isMarkdownMode ? 'Switch to Regular Mode' : 'Switch to Markdown Mode'}>
          <button
            onClick={handleToggleMarkdown}
            className="p-2 rounded-full text-white transition hover:bg-white/20"
          >
            <MarkdownIcon />
          </button>
        </Tooltip>

        <Tooltip text="New Note">
          <button
            onClick={handleCreate}
            className="p-2 rounded-full text-white transition hover:bg-white/20"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-7 w-7"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
        </Tooltip>
      </div>
    </div>
  );
}