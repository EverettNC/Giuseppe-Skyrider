import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// "Nothing Vital Lives Below Root" - Flattened Local Store Imports
import { useNotesStore, Note, BookChapter } from './GiuseppeNotesStore';
import { useGiovanniStore } from './GiovanniStore';
import {
  Book,
  BookOpen,
  Star,
  Calendar,
  Tag,
  TrendingUp,
  Heart,
  Brain,
  Sparkles,
  ChevronRight,
  Plus,
  X,
  Download,
} from 'lucide-react';

// Flattened UI Primitive Imports
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';

const GiuseppeBook: React.FC = () => {
  const {
    notes,
    bookChapters,
    getBookmarkedNotes,
    createChapter,
    exportToMarkdown,
  } = useNotesStore();

  const { speak } = useGiovanniStore();

  const [selectedChapter, setSelectedChapter] = useState<BookChapter | null>(null);
  const [showCreateChapter, setShowCreateChapter] = useState(false);
  const [newChapterTitle, setNewChapterTitle] = useState('');
  const [selectedNotes, setSelectedNotes] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'timeline' | 'chapters' | 'insights'>('timeline');

  const bookmarkedNotes = getBookmarkedNotes();

  // Get stats
  const stats = {
    totalNotes: notes.length,
    bookmarked: bookmarkedNotes.length,
    chapters: bookChapters.length,
    voiceNotes: notes.filter(n => n.type === 'voice').length,
    ideas: notes.filter(n => n.type === 'idea').length,
    memories: notes.filter(n => n.type === 'memory').length,
  };

  // Group notes by date
  const notesByDate: { [key: string]: Note[] } = {};
  notes.forEach(note => {
    const date = new Date(note.timestamp).toLocaleDateString();
    if (!notesByDate[date]) {
      notesByDate[date] = [];
    }
    notesByDate[date].push(note);
  });

  // Get most used tags
  const tagCounts: { [key: string]: number } = {};
  notes.forEach(note => {
    note.tags.forEach(tag => {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    });
  });
  const topTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const handleCreateChapter = () => {
    if (!newChapterTitle.trim() || selectedNotes.length === 0) {
      speak("Boss, I need a title and some notes to create a chapter!", 'sassy');
      return;
    }

    createChapter(newChapterTitle.trim(), selectedNotes);
    speak(`Chapter "${newChapterTitle}" created! Your book is coming together beautifully.`, 'hype');

    setNewChapterTitle('');
    setSelectedNotes([]);
    setShowCreateChapter(false);
  };

  const toggleNoteSelection = (noteId: string) => {
    setSelectedNotes(prev =>
      prev.includes(noteId)
        ? prev.filter(id => id !== noteId)
        : [...prev, noteId]
    );
  };

  const handleExport = () => {
    const markdown = exportToMarkdown();
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `giuseppe-book-${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);

    speak("Your complete book has been exported! That's a masterpiece right there, boss.", 'hype');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950 p-6 text-gray-100">
      {/* Animated hardware background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-20">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-purple-400 rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: 0.1,
            }}
            animate={{
              y: [null, Math.random() * window.innerHeight],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <BookOpen className="w-12 h-12 text-purple-400" />
            <h1 className="text-6xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent tracking-tighter">
              The Book
            </h1>
            <Sparkles className="w-12 h-12 text-pink-400" />
          </div>
          <p className="text-gray-400 text-xl mb-2 font-medium">
            Your journey, your memories, your masterpiece.
          </p>
          <p className="text-purple-400/80 text-sm italic font-mono uppercase tracking-widest">
            "Sovereign Memory Keeper - Giuseppe Skyrider"
          </p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {[
            { label: 'Total Notes', value: stats.totalNotes, icon: Book, color: 'purple' },
            { label: 'Bookmarked', value: stats.bookmarked, icon: Star, color: 'yellow' },
            { label: 'Chapters', value: stats.chapters, icon: BookOpen, color: 'pink' },
            { label: 'Voice Notes', value: stats.voiceNotes, icon: Brain, color: 'blue' },
            { label: 'Ideas', value: stats.ideas, icon: Sparkles, color: 'green' },
            { label: 'Memories', value: stats.memories, icon: Heart, color: 'red' },
          ].map((stat, idx) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <Card className="bg-gray-900/50 backdrop-blur-xl border-purple-500/20 hover:border-purple-500/40 transition-all group">
                <CardContent className="p-4 text-center">
                  <stat.icon className={`w-8 h-8 mx-auto mb-2 text-${stat.color}-400 group-hover:scale-110 transition-transform`} />
                  <div className={`text-3xl font-bold text-${stat.color}-400`}>
                    {stat.value}
                  </div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-tighter font-bold">{stat.label}</div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* View Mode Selector */}
        <div className="flex gap-2 justify-center mb-8">
          {[
            { mode: 'timeline', label: 'Timeline', icon: Calendar },
            { mode: 'chapters', label: 'Chapters', icon: BookOpen },
            { mode: 'insights', label: 'Insights', icon: TrendingUp },
          ].map(({ mode, label, icon: Icon }) => (
            <Button
              key={mode}
              variant={viewMode === mode ? 'default' : 'ghost'}
              onClick={() => setViewMode(mode as any)}
              className={`${
                viewMode === mode
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                  : 'text-gray-400 hover:bg-gray-900'
              } font-bold uppercase tracking-tighter`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {label}
            </Button>
          ))}
        </div>

        {/* Timeline View */}
        {viewMode === 'timeline' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-8"
          >
            {Object.entries(notesByDate).map(([date, dayNotes]) => (
              <div key={date}>
                <h3 className="text-2xl font-bold text-purple-400 mb-4 flex items-center gap-2 tracking-tight">
                  <Calendar className="w-6 h-6" />
                  {date}
                  <span className="text-xs text-gray-600 font-mono">[{dayNotes.length} ENTRIES]</span>
                </h3>
                <div className="space-y-3">
                  {dayNotes.map(note => (
                    <motion.div
                      key={note.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="relative pl-8 border-l-2 border-purple-500/20"
                    >
                      <div className="absolute -left-[9px] top-2 w-4 h-4 rounded-full bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.5)]" />
                      <Card className="bg-gray-900/40 backdrop-blur-md border-gray-800 hover:border-purple-500/30 transition-colors">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-black text-purple-400 uppercase tracking-widest">{note.type}</span>
                              <span className="text-[10px] text-gray-600 font-mono">
                                {new Date(note.timestamp).toLocaleTimeString()}
                              </span>
                              {note.bookmarked && <Star className="w-3 h-3 text-yellow-400 fill-yellow-400 animate-pulse" />}
                            </div>
                            {showCreateChapter && (
                              <input
                                type="checkbox"
                                checked={selectedNotes.includes(note.id)}
                                onChange={() => toggleNoteSelection(note.id)}
                                className="w-4 h-4 accent-purple-500 cursor-pointer"
                              />
                            )}
                          </div>
                          <p className="text-gray-300 leading-relaxed font-medium">{note.content}</p>
                          {note.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-3">
                              {note.tags.map(tag => (
                                <span
                                  key={tag}
                                  className="text-[10px] bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded font-bold uppercase"
                                >
                                  #{tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </div>
            ))}

            {notes.length === 0 && (
              <div className="text-center py-20">
                <Book className="w-24 h-24 mx-auto text-gray-800 mb-4" />
                <p className="text-gray-600 text-xl font-bold uppercase tracking-widest">The vault is silent.</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Chapters View */}
        {viewMode === 'chapters' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-black text-purple-400 uppercase tracking-tighter">Sovereign Chapters</h2>
              <Button
                onClick={() => setShowCreateChapter(!showCreateChapter)}
                className="bg-gradient-to-r from-purple-500 to-pink-500 font-bold"
              >
                {showCreateChapter ? <X className="w-4 h-4 mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
                {showCreateChapter ? 'Cancel Build' : 'Create New Chapter'}
              </Button>
            </div>

            {showCreateChapter && (
              <Card className="bg-gray-900/60 backdrop-blur-2xl border-purple-500/40 shadow-2xl">
                <CardHeader>
                  <CardTitle className="text-purple-400 uppercase tracking-widest text-sm">Chapter Construction</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Input
                    value={newChapterTitle}
                    onChange={(e) => setNewChapterTitle(e.target.value)}
                    placeholder="Chapter title..."
                    className="bg-gray-950 border-purple-500/30 text-lg font-bold"
                  />
                  <div className="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
                    <p className="text-xs text-purple-300 font-mono">
                      STATUS: {selectedNotes.length} node(s) selected for linkage.
                    </p>
                  </div>
                  <Button
                    onClick={handleCreateChapter}
                    disabled={!newChapterTitle.trim() || selectedNotes.length === 0}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-lg font-black italic shadow-lg shadow-purple-500/20"
                  >
                    DEPLOY CHAPTER
                  </Button>
                </CardContent>
              </Card>
            )}

            <div className="grid gap-4">
              {bookChapters.map((chapter, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card
                    className="bg-gray-900/40 backdrop-blur-md border-gray-800 cursor-pointer hover:border-purple-500/40 transition-all"
                    onClick={() => setSelectedChapter(selectedChapter?.title === chapter.title ? null : chapter)}
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-3">
                          <BookOpen className="w-6 h-6 text-purple-400" />
                          <span className="text-purple-400 font-bold">Chapter {idx + 1}: {chapter.title}</span>
                        </span>
                        <ChevronRight
                          className={`w-5 h-5 text-purple-400 transition-transform ${
                            selectedChapter?.title === chapter.title ? 'rotate-90' : ''
                          }`}
                        />
                      </CardTitle>
                    </CardHeader>
                    <AnimatePresence>
                      {selectedChapter?.title === chapter.title && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                        >
                          <CardContent className="space-y-3 pb-6">
                            <p className="text-[10px] text-gray-500 font-mono uppercase tracking-widest border-b border-gray-800 pb-2">
                              Created: {new Date(chapter.createdAt).toLocaleDateString()} • {chapter.notes.length} notes in mesh
                            </p>
                            {chapter.notes.map(note => (
                              <div
                                key={note.id}
                                className="bg-gray-950/50 rounded p-4 border-l-2 border-purple-500/50 hover:bg-gray-950 transition-colors"
                              >
                                <div className="flex items-center gap-2 mb-2 text-[10px] text-gray-600 font-mono uppercase">
                                  <span className="text-purple-400 font-black">{note.type}</span>
                                  <span>•</span>
                                  <span>{new Date(note.timestamp).toLocaleString()}</span>
                                </div>
                                <p className="text-gray-300 text-sm leading-relaxed">{note.content}</p>
                              </div>
                            ))}
                          </CardContent>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </Card>
                </motion.div>
              ))}
            </div>

            {bookChapters.length === 0 && !showCreateChapter && (
              <div className="text-center py-20">
                <BookOpen className="w-24 h-24 mx-auto text-gray-800 mb-4 opacity-50" />
                <p className="text-gray-600 text-xl font-black uppercase tracking-tighter">No chapters mapped.</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Insights View */}
        {viewMode === 'insights' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <Card className="bg-gray-900/40 backdrop-blur-xl border-gray-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-purple-400 font-black uppercase tracking-widest text-sm">
                  <Tag className="w-4 h-4" />
                  Dominant Tags
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-3">
                  {topTags.map(([tag, count]) => (
                    <motion.div
                      key={tag}
                      whileHover={{ scale: 1.05 }}
                      className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-full px-4 py-2 flex items-center gap-2 shadow-lg shadow-purple-500/10"
                    >
                      <span className="text-white font-black italic">#{tag}</span>
                      <span className="text-white/70 text-xs font-mono">[{count}]</span>
                    </motion.div>
                  ))}
                  {topTags.length === 0 && (
                    <p className="text-gray-600 italic">Cognitive metadata awaiting input.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900/40 backdrop-blur-xl border-gray-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-yellow-400 font-black uppercase tracking-widest text-sm">
                  <Star className="w-4 h-4" />
                  Sovereign Highlights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {bookmarkedNotes.map(note => (
                  <div
                    key={note.id}
                    className="bg-gradient-to-r from-yellow-500/10 to-transparent border-l-2 border-yellow-500/40 rounded-r p-4"
                  >
                    <div className="flex items-center gap-2 mb-2 text-[10px] font-mono text-yellow-400 uppercase tracking-widest font-black">
                      <Star className="w-3 h-3 fill-yellow-400" />
                      <span>{note.type}</span>
                      <span className="text-gray-600">//</span>
                      <span>{new Date(note.timestamp).toLocaleString()}</span>
                    </div>
                    <p className="text-gray-300 font-medium italic">"{note.content}"</p>
                  </div>
                ))}
                {bookmarkedNotes.length === 0 && (
                  <p className="text-gray-600 text-center py-8 italic uppercase tracking-tighter">
                    No bookmarks detected in the mesh.
                  </p>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Export Button */}
        {notes.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed bottom-8 right-8"
          >
            <Button
              onClick={handleExport}
              className="bg-gradient-to-r from-purple-500 to-pink-500 shadow-[0_0_30px_rgba(168,85,247,0.4)] hover:shadow-[0_0_50px_rgba(168,85,247,0.6)] transition-all font-black italic text-lg px-8 py-6 h-auto"
            >
              <Download className="w-6 h-6 mr-3" />
              EXPORT MANUSCRIPT
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default GiuseppeBook;
