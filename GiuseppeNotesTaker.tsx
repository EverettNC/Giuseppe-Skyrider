import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNotesStore, Note } from './GiuseppeNotesStore';
import { useGiovanniStore } from './GiovanniStore';
import {
  Mic,
  MicOff,
  Book,
  Sparkles,
  Bookmark,
  Trash2,
  Download,
  Eye,
  EyeOff,
  Zap,
  Brain,
  Heart,
  Lightbulb,
  MessageCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';

// Speech Recognition types
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

const GiuseppeNotesTaker: React.FC = () => {
  const {
    notes,
    isRecording,
    isAutoNote,
    addNote,
    deleteNote,
    toggleBookmark,
    startRecording,
    stopRecording,
    toggleAutoNote,
    exportToMarkdown,
  } = useNotesStore();

  const { addMessage, speak } = useGiovanniStore();

  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [selectedType, setSelectedType] = useState<Note['type']>('voice');
  const [isListening, setIsListening] = useState(false);
  const [showNotes, setShowNotes] = useState(true);
  const [filterType, setFilterType] = useState<Note['type'] | 'all'>('all');

  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: any) => {
          let interim = '';
          let final = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              final += transcript + ' ';
            } else {
              interim += transcript;
            }
          }

          if (final) {
            setTranscript((prev) => prev + final);

            // Auto-save note after 3 seconds of silence
            if (isAutoNote) {
              setTimeout(() => {
                if (final.trim()) {
                  saveQuickNote(final.trim(), 'voice');
                }
              }, 3000);
            }
          }

          setInterimTranscript(interim);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          if (event.error === 'no-speech') {
            // Restart if no speech detected
            if (isListening) {
              recognitionRef.current.start();
            }
          }
        };

        recognitionRef.current.onend = () => {
          if (isListening) {
            // Auto-restart when auto-note is enabled
            recognitionRef.current.start();
          }
        };
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isAutoNote, isListening]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      speak("Sorry boss, your browser doesn't support voice recognition. But I'm still here taking notes!", 'sassy');
      return;
    }

    if (!isListening) {
      setIsListening(true);
      startRecording();
      recognitionRef.current.start();
      speak("I'm listening, boss. Speak your mind, I got you.", 'swagger');
    } else {
      setIsListening(false);
      const duration = stopRecording();
      recognitionRef.current.stop();

      if (transcript.trim()) {
        saveNote(transcript.trim(), selectedType, duration);
        speak("Got it all down. That was fire, boss.", 'hype');
        setTranscript('');
      }
      setInterimTranscript('');
    }
  };

  const saveNote = (content: string, type: Note['type'], duration?: number) => {
    if (!content.trim()) return;

    const mood = useGiovanniStore.getState().mood;

    addNote({
      content,
      type,
      mood,
      tags: extractTags(content),
      bookmarked: false,
      recordingDuration: duration,
    });

    addMessage({
      text: `Noted! Filed under "${type}". ${getMotivationalQuip()}`,
      mood,
    });
  };

  const saveQuickNote = (content: string, type: Note['type']) => {
    if (!content.trim() || content.length < 10) return; // Ignore very short phrases

    const mood = useGiovanniStore.getState().mood;

    addNote({
      content,
      type,
      mood,
      tags: extractTags(content),
      bookmarked: false,
    });
  };

  const extractTags = (content: string): string[] => {
    const tags: string[] = [];

    // Extract hashtags
    const hashtagMatches = content.match(/#\w+/g);
    if (hashtagMatches) {
      tags.push(...hashtagMatches.map(tag => tag.slice(1)));
    }

    // Auto-tag based on keywords
    const keywords: { [key: string]: string[] } = {
      work: ['client', 'project', 'deadline', 'meeting', 'call'],
      creative: ['idea', 'creative', 'inspiration', 'design', 'art'],
      personal: ['feel', 'think', 'remember', 'note to self'],
      health: ['medication', 'water', 'exercise', 'sleep', 'health'],
      social: ['post', 'content', 'tiktok', 'instagram', 'video'],
    };

    const lowerContent = content.toLowerCase();
    Object.entries(keywords).forEach(([tag, words]) => {
      if (words.some(word => lowerContent.includes(word))) {
        tags.push(tag);
      }
    });

    return [...new Set(tags)]; // Remove duplicates
  };

  const getMotivationalQuip = (): string => {
    const quips = [
      "You're on fire today! 🔥",
      "That's going in the book!",
      "Future you is gonna thank present you.",
      "I see you building that empire!",
      "This is the content right here.",
      "Your brain is a goldmine, boss.",
    ];
    return quips[Math.floor(Math.random() * quips.length)];
  };

  const handleExport = () => {
    const markdown = exportToMarkdown();
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `giuseppe-notes-${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);

    speak("Your book has been downloaded! Look at all that wisdom, boss.", 'hype');
  };

  const filteredNotes = filterType === 'all'
    ? notes
    : notes.filter(note => note.type === filterType);

  const typeIcons: { [key in Note['type']]: React.ReactNode } = {
    voice: <Mic className="w-4 h-4" />,
    observation: <Eye className="w-4 h-4" />,
    reminder: <Zap className="w-4 h-4" />,
    idea: <Lightbulb className="w-4 h-4" />,
    memory: <Heart className="w-4 h-4" />,
  };

  const typeColors: { [key in Note['type']]: string } = {
    voice: 'from-purple-500 to-pink-500',
    observation: 'from-blue-500 to-cyan-500',
    reminder: 'from-yellow-500 to-orange-500',
    idea: 'from-green-500 to-emerald-500',
    memory: 'from-red-500 to-pink-500',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950 p-6">
      {/* Magical background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500 rounded-full filter blur-3xl opacity-20"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-500 rounded-full filter blur-3xl opacity-20"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.3, 0.2, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
        />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            <Brain className="w-10 h-10 text-purple-400" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              Giuseppe's Memory Bank
            </h1>
            <Sparkles className="w-10 h-10 text-pink-400" />
          </div>
          <p className="text-gray-400 text-lg">
            I'm always watching, always learning, always taking notes for your book.
          </p>
        </motion.div>

        {/* Recording Control Panel */}
        <Card className="mb-8 bg-gray-900/50 backdrop-blur-xl border-purple-500/30">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <MessageCircle className="w-6 h-6 text-purple-400" />
                Voice Capture
              </span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-normal text-gray-400">Auto-Note</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleAutoNote}
                  className={`${isAutoNote ? 'text-green-400' : 'text-gray-500'}`}
                >
                  {isAutoNote ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Recording Button */}
              <div className="flex justify-center">
                <motion.button
                  onClick={toggleListening}
                  className={`relative w-32 h-32 rounded-full flex items-center justify-center ${
                    isListening
                      ? 'bg-gradient-to-br from-red-500 to-pink-500'
                      : 'bg-gradient-to-br from-purple-500 to-pink-500'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  animate={isListening ? {
                    boxShadow: [
                      '0 0 0 0 rgba(236, 72, 153, 0.7)',
                      '0 0 0 20px rgba(236, 72, 153, 0)',
                    ],
                  } : {}}
                  transition={{
                    duration: 1.5,
                    repeat: isListening ? Infinity : 0,
                  }}
                >
                  {isListening ? (
                    <MicOff className="w-12 h-12 text-white" />
                  ) : (
                    <Mic className="w-12 h-12 text-white" />
                  )}
                </motion.button>
              </div>

              {/* Live Transcript */}
              <AnimatePresence>
                {(isListening || transcript || interimTranscript) && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-gray-800/50 rounded-lg p-4 min-h-24"
                  >
                    <p className="text-gray-300">
                      {transcript}
                      <span className="text-purple-400">{interimTranscript}</span>
                      {isListening && <span className="animate-pulse">|</span>}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Note Type Selector */}
              <div className="flex gap-2 justify-center flex-wrap">
                {(['voice', 'observation', 'reminder', 'idea', 'memory'] as Note['type'][]).map((type) => (
                  <Button
                    key={type}
                    variant={selectedType === type ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setSelectedType(type)}
                    className={`${
                      selectedType === type
                        ? `bg-gradient-to-r ${typeColors[type]} text-white`
                        : 'text-gray-400'
                    }`}
                  >
                    {typeIcons[type]}
                    <span className="ml-2 capitalize">{type}</span>
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notes Display */}
        <Card className="bg-gray-900/50 backdrop-blur-xl border-purple-500/30">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Book className="w-6 h-6 text-purple-400" />
                Your Notes ({filteredNotes.length})
              </div>
              <div className="flex gap-2">
                {/* Filter Buttons */}
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as Note['type'] | 'all')}
                  className="bg-gray-800 text-gray-300 rounded px-3 py-1 text-sm border border-purple-500/30"
                >
                  <option value="all">All Types</option>
                  <option value="voice">Voice</option>
                  <option value="observation">Observations</option>
                  <option value="reminder">Reminders</option>
                  <option value="idea">Ideas</option>
                  <option value="memory">Memories</option>
                </select>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleExport}
                  disabled={notes.length === 0}
                  className="text-purple-400 hover:text-purple-300"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Book
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowNotes(!showNotes)}
                  className="text-purple-400"
                >
                  {showNotes ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <AnimatePresence>
              {showNotes && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-3 max-h-[600px] overflow-y-auto"
                >
                  {filteredNotes.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                      <Brain className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p>No notes yet. Start talking, I'm listening!</p>
                    </div>
                  ) : (
                    filteredNotes.map((note) => (
                      <motion.div
                        key={note.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className={`bg-gradient-to-r ${typeColors[note.type]} p-0.5 rounded-lg`}
                      >
                        <div className="bg-gray-800 rounded-lg p-4">
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                {typeIcons[note.type]}
                                <span className="text-xs text-purple-400 capitalize">
                                  {note.type}
                                </span>
                                <span className="text-xs text-gray-500">
                                  {new Date(note.timestamp).toLocaleString()}
                                </span>
                                {note.recordingDuration && (
                                  <span className="text-xs text-gray-500">
                                    ({Math.round(note.recordingDuration)}s)
                                  </span>
                                )}
                              </div>
                              <p className="text-gray-300 mb-2">{note.content}</p>
                              {note.tags.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {note.tags.map((tag) => (
                                    <span
                                      key={tag}
                                      className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded"
                                    >
                                      #{tag}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => toggleBookmark(note.id)}
                                className={note.bookmarked ? 'text-yellow-400' : 'text-gray-500'}
                              >
                                <Bookmark className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => deleteNote(note.id)}
                                className="text-red-400 hover:text-red-300"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </CardContent>
        </Card>

        {/* Status indicator */}
        <AnimatePresence>
          {isAutoNote && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-purple-500/20 backdrop-blur-xl border border-purple-500/50 rounded-full px-6 py-3 flex items-center gap-3"
            >
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                }}
                className="w-3 h-3 rounded-full bg-green-400"
              />
              <span className="text-sm text-purple-200 font-medium">
                Giuseppe is watching & taking notes...
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default GiuseppeNotesTaker;
