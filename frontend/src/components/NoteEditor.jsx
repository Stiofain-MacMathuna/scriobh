import { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import '../styles/scrollbar.css';

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

function NoteEditor({ note, onChange, isMarkdownMode }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const [editorWidth, setEditorWidth] = useState(50);
  const [isReadyToSave, setIsReadyToSave] = useState(false);

  const containerRef = useRef(null);
  const noteIdRef = useRef(null);

  const debouncedTitle = useDebounce(title, 500);
  const debouncedContent = useDebounce(content, 500);

  
  useEffect(() => {
    if (note) {
      noteIdRef.current = note.id;
      setIsReadyToSave(false);

      setTitle(note.title);
      const newContent = note.content || '';
      setContent(newContent);

      const rawMarkup = marked(newContent);
      const sanitizedMarkup = DOMPurify.sanitize(rawMarkup);
      setHtmlContent(sanitizedMarkup);

      setIsReadyToSave(true);
    }
  }, [note]);

  useEffect(() => {
    async function saveNote() {
      if (!note || !note.id || !isReadyToSave) return;
      if (note.id !== noteIdRef.current) return;
      if (note.title === debouncedTitle && note.content === debouncedContent) return;

      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found. Cannot save note.');
        return;
      }

      console.log('Saving note:', {
        id: note.id,
        title: debouncedTitle,
        content: debouncedContent,
      });

      try {
        const res = await fetch(`http://localhost:8000/notes/${note.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            title: debouncedTitle,
            content: debouncedContent,
          }),
        });

        const responseBody = await res.json();
        console.log('Save response:', res.status, responseBody);

        if (!res.ok) {
          console.error('Failed to save note:', responseBody);
        } else {
        
          if (onChange) {
            onChange(responseBody);
          }
        }
      } catch (error) {
        console.error('Network error while saving:', error);
      }
    }

    saveNote();
  }, [debouncedTitle, debouncedContent]);

  const handleContentChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    const rawMarkup = marked(newContent);
    const sanitizedMarkup = DOMPurify.sanitize(rawMarkup);
    setHtmlContent(sanitizedMarkup);
  };

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
  };

  const handleMouseDown = (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = editorWidth;
    const containerWidth = containerRef.current.offsetWidth;

    const handleMouseMove = (moveEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const newWidth = ((startWidth * containerWidth / 100) + deltaX) / containerWidth * 100;
      if (newWidth > 10 && newWidth < 90) {
        setEditorWidth(newWidth);
      }
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