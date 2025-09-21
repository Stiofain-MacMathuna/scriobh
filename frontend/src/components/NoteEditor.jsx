import { useState, useEffect, useRef, useCallback } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import _ from 'lodash';
import '../styles/scrollbar.css';

const API_URL = import.meta.env.VITE_API_URL;

function NoteEditor({ note, onChange, isMarkdownMode }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const [editorWidth, setEditorWidth] = useState(50);
  const [isReadyToSave, setIsReadyToSave] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const containerRef = useRef(null);
  const noteIdRef = useRef(null);
  const lastSavedRef = useRef({ title: '', content: '' });

  // Initialize note
  useEffect(() => {
    if (!note) return;

    noteIdRef.current = note.id;
    setIsReadyToSave(false);

    setTitle(note.title);
    const newContent = note.content || '';
    setContent(newContent);

    const rawMarkup = marked(newContent);
    const sanitizedMarkup = DOMPurify.sanitize(rawMarkup);
    setHtmlContent(sanitizedMarkup);

    lastSavedRef.current = { title: note.title, content: newContent };
    setIsReadyToSave(true);
  }, [note]);

  // Debounced save function
  const saveNoteDebounced = useCallback(
    _.debounce(async (id, titleToSave, contentToSave) => {
      const token = localStorage.getItem('token');
      if (!token) return;

      setIsSaving(true);
      try {
        const res = await fetch(`${API_URL}/notes/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ title: titleToSave, content: contentToSave }),
        });

        const responseBody = await res.json();
        if (!res.ok) {
          console.error('Failed to save note:', responseBody);
        } else {
          lastSavedRef.current = { title: titleToSave, content: contentToSave };
          if (onChange) onChange(responseBody);
        }
      } catch (err) {
        console.error('Network error while saving:', err);
      } finally {
        setIsSaving(false);
      }
    }, 1000),
    []
  );

  // Handle title change
  const handleTitleChange = (e) => {
    const newTitle = e.target.value;
    setTitle(newTitle);

    if (!isReadyToSave || !note?.id) return;
    if (
      newTitle !== lastSavedRef.current.title ||
      content !== lastSavedRef.current.content
    ) {
      saveNoteDebounced(note.id, newTitle, content);
    }
  };

  // Handle content change
  const handleContentChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);

    const rawMarkup = marked(newContent);
    const sanitizedMarkup = DOMPurify.sanitize(rawMarkup);
    setHtmlContent(sanitizedMarkup);

    if (!isReadyToSave || !note?.id) return;
    if (title !== lastSavedRef.current.title || newContent !== lastSavedRef.current.content) {
      saveNoteDebounced(note.id, title, newContent);
    }
  };

  // Handle editor resize
  const handleMouseDown = (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = editorWidth;
    const containerWidth = containerRef.current.offsetWidth;

    const handleMouseMove = (moveEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const newWidth = ((startWidth * containerWidth) / 100 + deltaX) / containerWidth * 100;
      if (newWidth > 10 && newWidth < 90) setEditorWidth(newWidth);
    };

    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div className="flex flex-col h-full w-full p-6 text-white" ref={containerRef}>
      <div className="flex justify-between items-center mb-4">
        <input
          type="text"
          value={title}
          onChange={handleTitleChange}
          className="w-full px-4 text-2xl font-semibold placeholder-gray-400 border-b border-white/10 pb-2 focus:outline-none bg-transparent rounded"
          placeholder="Note title"
        />
        {isSaving && <div className="text-sm text-gray-400 ml-4">Saving...</div>}
      </div>

      {isMarkdownMode ? (
        <div className="flex flex-1 overflow-hidden">
          <div className="flex flex-col overflow-y-auto" style={{ width: `${editorWidth}%` }}>
            <textarea
              value={content}
              onChange={handleContentChange}
              className="flex-1 w-full px-4 py-2 resize-none focus:outline-none bg-transparent placeholder-gray-400 rounded overflow-auto custom-scrollbar"
              placeholder="Start writing your note here..."
            />
          </div>

          <div
            className="w-2 bg-gray-600 cursor-col-resize hover:bg-gray-400 transition-colors"
            onMouseDown={handleMouseDown}
          ></div>

          <div className="flex flex-col overflow-y-auto" style={{ width: `${100 - editorWidth}%` }}>
            <div
              className="flex-1 w-full pr-4 py-2 bg-[#1e293b] rounded overflow-y-auto prose prose-invert break-words border-l border-white/10 pl-6 custom-scrollbar max-w-none"
              dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
          </div>
        </div>
      ) : (
        <textarea
          value={content}
          onChange={handleContentChange}
          className="flex-1 w-full px-4 py-2 resize-none focus:outline-none bg-transparent placeholder-gray-400 rounded overflow-auto custom-scrollbar"
          placeholder="Start writing your note here..."
        />
      )}
    </div>
  );
}

export default NoteEditor;