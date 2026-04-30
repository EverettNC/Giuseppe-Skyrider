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
// "Nothing Vital Lives Below Root" - Imports flattened to root directory
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';

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
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;

        recognitionRef.current.onresult = (event: any) => {
          let currentTranscript = '';
          let currentInterim = '';

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              currentTranscript += event.results[i][0].transcript;
            } else {
              currentInterim += event.results[i][0].transcript;
            }
          }

          setInterimTranscript(currentInterim);
          if (currentTranscript) {
            setTranscript((prev) => prev + ' ' + currentTranscript);
            resetSilenceTimer();
          }
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error', event.error);
          setIsListening(false);
          stopRecording();
        };

        recognitionRef.current.onend = () => {
          if (isRecording) {
            recognitionRef.current.start();
          } else {
            setIsListening(false);
          }
        };
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }
    };
  }, [isRecording]);

  const resetSilenceTimer = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
    // Auto-save after 3 seconds of silence if auto-note is on
    if (isAutoNote) {
      silenceTimerRef.current = setTimeout(() => {
        handleSaveNote();
      }, 3000);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      stopRecording();
      if (transcript.trim()) {
        handleSaveNote();
      }
    } else {
      setTranscript('');
      setInterimTranscript('');
      recognitionRef.current?.start();
      setIsListening(true);
      startRecording();
    }
  };

  const handleSaveNote = () => {
    const finalContent = transcript.trim();
    if (!finalContent) return;

    addNote({
      content: finalContent,
      type: selectedType,
      mood: 'swagger',
      tags: [],
      bookmarked: false,
    });

    speak(`Caught that ${selectedType}. It's in the vault.`, 'swagger');

    setTranscript('');
    setInterimTranscript('');
  };

  const filteredNotes = notes
    .filter(n => filterType === 'all' || n.type === filterType)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  const getTypeIcon = (type: Note['type']) => {
    switch (type) {
      case 'voice': return <Mic className="w-4 h-4 text-blue-400" />;
      case 'idea': return <Lightbulb className="w-4 h-4 text-yellow-400" />;
      case 'observation': return <Eye className="w-4 h-4 text-green-400" />;
      case 'memory': return <Brain className="w-4 h-4 text-purple-400" />;
      case 'reminder': return <Zap className="w-4 h-4 text-giovanni-accent" />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 p-6 overflow-hidden">
      {/* Left Column: Input & Controls */}
      <div className="w-1/3 flex flex-col gap-6 pr-6 border-r border-gray-800">
        <div>
          <h1 className="text-3xl font-bold text-giovanni-primary mb-2 flex items-center gap-2">
            <Book className="w-8 h-8" />
            Giuseppe Skyrider
          </h1>
          <p className="text-gray-400 text-sm">Sovereign Note Taker & Cognitive Vault</p>
        </div>

        <Card className="flex-1 flex flex-col bg-gray-900/50">
          <CardHeader>
            <CardTitle className="flex justify-between items-center text-lg">
              Capture Thought
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleAutoNote}
                className={isAutoNote ? 'text-giovanni-accent' : 'text-gray-500'}
              >
                <Zap className="w-4 h-4 mr-2" />
                Auto-Catch
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col gap-4">
            {/* Type Selector */}
            <div className="flex flex-wrap gap-2">
              {(['voice', 'idea', 'observation', 'memory', 'reminder'] as Note['type'][]).map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors flex items-center gap-1
                    ${selectedType === type
                      ? 'bg-gray-800 text-white border border-gray-600'
                      : 'bg-gray-950 text-gray-400 border border-transparent hover:bg-gray-900'
                    }`}
                >
                  {getTypeIcon(type)}
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>

            {/* Active Recording Area */}
            <div className="flex-1 bg-gray-950 rounded-lg p-4 relative overflow-y-auto border border-gray-800">
              {transcript ? (
                <div className="space-y-2">
                  <p className="text-gray-200 leading-relaxed">{transcript}</p>
                  <p className="text-gray-500 italic">{interimTranscript}</p>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-600 flex-col gap-4">
                  <MicOff className="w-12 h-12 opacity-20" />
                  <p>Silence.</p>
                </div>
              )}

              {/* Recording Indicator */}
              <AnimatePresence>
                {isListening && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute top-4 right-4 flex items-center gap-2"
                  >
                    <span className="text-xs text-red-400 font-medium tracking-widest uppercase">Recording</span>
                    <motion.div
                      animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                      className="w-2 h-2 rounded-full bg-red-500"
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Main Controls */}
            <div className="grid grid-cols-2 gap-4">
              <Button
                onClick={toggleListening}
                variant={isListening ? 'destructive' : 'default'}
                className="h-14 text-lg font-semibold tracking-wide"
              >
                {isListening ? (
                  <>
                    <MicOff className="w-5 h-5 mr-2" /> Stop Recording
                  </>
                ) : (
                  <>
                    <Mic className="w-5 h-5 mr-2" /> Start Recording
                  </>
                )}
              </Button>
              <Button
                onClick={handleSaveNote}
                disabled={!transcript.trim()}
                className="h-14 bg-gray-800 hover:bg-gray-700 text-white text-lg font-semibold tracking-wide"
              >
                <Bookmark className="w-5 h-5 mr-2" /> Lock It In
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right Column: Vault / History */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-2">
            <button
              onClick={() => setFilterType('all')}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${filterType === 'all' ? 'bg-giovanni-primary text-white' : 'bg-gray-900 text-gray-400 hover:bg-gray-800'}`}
            >
              All Notes
            </button>
            <button
              onClick={() => setFilterType('idea')}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${filterType === 'idea' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-900 text-gray-400 hover:bg-gray-800'}`}
            >
              Ideas
            </button>
            <button
              onClick={() => setFilterType('memory')}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${filterType === 'memory' ? 'bg-purple-500/20 text-purple-400' : 'bg-gray-900 text-gray-400 hover:bg-gray-800'}`}
            >
              Memories
            </button>
          </div>
          
          <div className="flex gap-4">
            <Button variant="ghost" onClick={() => setShowNotes(!showNotes)} className="text-gray-400">
              {showNotes ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        <Card className="flex-1 bg-transparent border-none shadow-none overflow-hidden flex flex-col">
          <CardContent className="flex-1 overflow-y-auto pr-4 p-0 space-y-4">
            <AnimatePresence>
              {showNotes && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="space-y-4"
                >
                  {filteredNotes.length === 0 ? (
                    <div className="text-center py-20 text-gray-600">
                      <Book className="w-16 h-16 mx-auto mb-4 opacity-20" />
                      <p className="text-lg">The vault is empty.</p>
                      <p className="text-sm">Start recording to lay down reality.</p>
                    </div>
                  ) : (
                    filteredNotes.map((note) => (
                      <motion.div
                        key={note.id}
                        layout
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className={`p-5 rounded-lg border ${note.bookmarked ? 'bg-gray-800/80 border-giovanni-accent' : 'bg-gray-900/40 border-gray-800 hover:bg-gray-900/60'}`}
                      >
                        <div className="flex justify-between items-start gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-3">
                              {getTypeIcon(note.type)}
                              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                                {note.type}
                              </span>
                              <span className="text-xs text-gray-600">
                                {new Date(note.timestamp).toLocaleString()}
                              </span>
                            </div>
                            <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                              {note.content}
                            </p>
                          </div>
                          <div className="flex flex-col gap-2">
                            <div className="flex gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => toggleBookmark(note.id)}
                                className={note.bookmarked ? 'text-giovanni-accent' : 'text-gray-500 hover:text-gray-300'}
                              >
                                <Bookmark className={`w-4 h-4 ${note.bookmarked ? 'fill-current' : ''}`} />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => deleteNote(note.id)}
                                className="text-gray-600 hover:text-red-400 hover:bg-red-400/10"
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
