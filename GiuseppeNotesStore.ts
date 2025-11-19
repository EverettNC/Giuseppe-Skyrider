import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Note {
  id: string;
  content: string;
  timestamp: Date;
  type: 'voice' | 'observation' | 'reminder' | 'idea' | 'memory';
  mood: 'swagger' | 'motivational' | 'sassy' | 'caring' | 'hype';
  tags: string[];
  bookmarked: boolean;
  recordingDuration?: number; // in seconds
}

export interface BookChapter {
  title: string;
  notes: Note[];
  createdAt: Date;
  summary?: string;
}

interface NotesStore {
  notes: Note[];
  isRecording: boolean;
  isAutoNote: boolean;
  currentRecordingStart: Date | null;
  bookChapters: BookChapter[];

  // Actions
  addNote: (note: Omit<Note, 'id' | 'timestamp'>) => void;
  deleteNote: (id: string) => void;
  toggleBookmark: (id: string) => void;
  updateNote: (id: string, updates: Partial<Note>) => void;
  startRecording: () => void;
  stopRecording: () => void;
  toggleAutoNote: () => void;
  createChapter: (title: string, noteIds: string[]) => void;
  getNotesByType: (type: Note['type']) => Note[];
  getNotesByDateRange: (start: Date, end: Date) => Note[];
  getBookmarkedNotes: () => Note[];
  clearAllNotes: () => void;
  exportToMarkdown: () => string;
}

export const useNotesStore = create<NotesStore>()(
  persist(
    (set, get) => ({
      notes: [],
      isRecording: false,
      isAutoNote: true, // Auto-note taking enabled by default
      currentRecordingStart: null,
      bookChapters: [],

      addNote: (noteData) => {
        const newNote: Note = {
          ...noteData,
          id: `note_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
        };

        set((state) => ({
          notes: [newNote, ...state.notes], // Newest first
        }));
      },

      deleteNote: (id) => {
        set((state) => ({
          notes: state.notes.filter((note) => note.id !== id),
        }));
      },

      toggleBookmark: (id) => {
        set((state) => ({
          notes: state.notes.map((note) =>
            note.id === id ? { ...note, bookmarked: !note.bookmarked } : note
          ),
        }));
      },

      updateNote: (id, updates) => {
        set((state) => ({
          notes: state.notes.map((note) =>
            note.id === id ? { ...note, ...updates } : note
          ),
        }));
      },

      startRecording: () => {
        set({
          isRecording: true,
          currentRecordingStart: new Date(),
        });
      },

      stopRecording: () => {
        const { currentRecordingStart } = get();
        const duration = currentRecordingStart
          ? (new Date().getTime() - currentRecordingStart.getTime()) / 1000
          : 0;

        set({
          isRecording: false,
          currentRecordingStart: null,
        });

        return duration;
      },

      toggleAutoNote: () => {
        set((state) => ({
          isAutoNote: !state.isAutoNote,
        }));
      },

      createChapter: (title, noteIds) => {
        const { notes } = get();
        const chapterNotes = notes.filter((note) => noteIds.includes(note.id));

        const newChapter: BookChapter = {
          title,
          notes: chapterNotes,
          createdAt: new Date(),
        };

        set((state) => ({
          bookChapters: [...state.bookChapters, newChapter],
        }));
      },

      getNotesByType: (type) => {
        return get().notes.filter((note) => note.type === type);
      },

      getNotesByDateRange: (start, end) => {
        return get().notes.filter((note) => {
          const noteDate = new Date(note.timestamp);
          return noteDate >= start && noteDate <= end;
        });
      },

      getBookmarkedNotes: () => {
        return get().notes.filter((note) => note.bookmarked);
      },

      clearAllNotes: () => {
        set({ notes: [], bookChapters: [] });
      },

      exportToMarkdown: () => {
        const { notes, bookChapters } = get();
        let markdown = '# Giuseppe\'s Book of Memories\n\n';
        markdown += `*Generated on ${new Date().toLocaleDateString()}*\n\n`;
        markdown += '---\n\n';

        // Export chapters
        if (bookChapters.length > 0) {
          markdown += '## Chapters\n\n';
          bookChapters.forEach((chapter, idx) => {
            markdown += `### Chapter ${idx + 1}: ${chapter.title}\n\n`;
            markdown += `*Created: ${new Date(chapter.createdAt).toLocaleDateString()}*\n\n`;

            chapter.notes.forEach((note) => {
              markdown += `- **${note.type.toUpperCase()}** (${new Date(note.timestamp).toLocaleString()}): ${note.content}\n`;
              if (note.tags.length > 0) {
                markdown += `  - Tags: ${note.tags.join(', ')}\n`;
              }
            });
            markdown += '\n';
          });
        }

        // Export all notes by type
        const noteTypes: Note['type'][] = ['voice', 'observation', 'reminder', 'idea', 'memory'];

        noteTypes.forEach((type) => {
          const typeNotes = notes.filter((n) => n.type === type);
          if (typeNotes.length > 0) {
            markdown += `## ${type.charAt(0).toUpperCase() + type.slice(1)}s\n\n`;
            typeNotes.forEach((note) => {
              const bookmarkIcon = note.bookmarked ? '⭐ ' : '';
              markdown += `- ${bookmarkIcon}**${new Date(note.timestamp).toLocaleString()}**: ${note.content}\n`;
              if (note.tags.length > 0) {
                markdown += `  - Tags: ${note.tags.join(', ')}\n`;
              }
            });
            markdown += '\n';
          }
        });

        return markdown;
      },
    }),
    {
      name: 'giuseppe-notes-storage',
      version: 1,
    }
  )
);
