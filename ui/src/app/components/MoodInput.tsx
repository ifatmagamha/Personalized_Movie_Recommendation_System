import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, ArrowLeft, Send } from 'lucide-react';

interface MoodInputProps {
  onSubmit: (input: string, isVoice: boolean) => void;
  onBack: () => void;
}

export function MoodInput({ onSubmit, onBack }: MoodInputProps) {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [activeMode, setActiveMode] = useState<'text' | 'voice'>('text');

  const suggestions = [
    '"feeling melancholic, want something slow and beautiful"',
    '"restless energy, need something tense but not scary"',
  ];

  const handleVoiceToggle = () => {
    // Mock voice input - in real app would use Web Speech API
    if (!isListening) {
      setIsListening(true);
      setActiveMode('voice');
      
      // Simulate voice recognition
      setTimeout(() => {
        const mockInput = 'feeling contemplative and want something slow';
        setInput(mockInput);
        setIsListening(false);
      }, 2000);
    } else {
      setIsListening(false);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (input.trim()) {
      onSubmit(input.trim(), activeMode === 'voice');
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 relative overflow-hidden">
      {/* Subtle neon accent background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 right-1/3 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 left-1/4 w-80 h-80 bg-purple-500/8 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <div className="container mx-auto px-6 py-6 relative z-10">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-neutral-400 hover:text-neutral-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">back</span>
        </button>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-16 md:py-20 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto"
        >
          <h2 className="mb-4 text-neutral-50">
            how are you feeling?
          </h2>
          
          <p className="text-lg text-neutral-400 mb-12">
            describe your mood, we'll find something that fits
          </p>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="mb-16">
            <div className="relative mb-4">
              <textarea
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  setActiveMode('text');
                }}
                placeholder="i'm feeling..."
                className="w-full h-48 px-6 py-6 bg-neutral-900/50 border border-neutral-800 focus:border-neutral-600 focus:outline-none resize-none text-lg text-neutral-200 placeholder:text-neutral-700 backdrop-blur-sm"
                disabled={isListening}
              />

              {/* Voice Input Indicator */}
              <AnimatePresence>
                {isListening && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-neutral-900 border-2 border-pink-500 flex items-center justify-center"
                  >
                    <div className="text-center">
                      <motion.div
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ repeat: Infinity, duration: 1.5 }}
                        className="w-16 h-16 mx-auto mb-4 flex items-center justify-center"
                      >
                        <Mic className="w-8 h-8 text-pink-500" />
                      </motion.div>
                      <p className="text-sm text-neutral-400">listening...</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Bottom controls inside textarea */}
              <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between">
                <button
                  type="button"
                  onClick={handleVoiceToggle}
                  className={`flex items-center gap-2 text-sm transition-colors ${
                    isListening
                      ? 'text-pink-500'
                      : 'text-neutral-500 hover:text-neutral-300'
                  }`}
                >
                  <Mic className="w-4 h-4" />
                  <span>use voice</span>
                </button>

                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="flex items-center gap-2 text-sm text-neutral-400 hover:text-neutral-200 disabled:text-neutral-700 disabled:cursor-not-allowed transition-colors"
                >
                  <span>find movies</span>
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </form>

          {/* Suggestions */}
          <div>
            <p className="text-xs text-neutral-600 mb-4 uppercase tracking-wider">
              OR TRY THESE
            </p>
            <div className="flex flex-col gap-3">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setInput(suggestion.replace(/"/g, ''));
                    setActiveMode('text');
                  }}
                  className="px-6 py-4 text-left text-sm border border-neutral-800 hover:border-neutral-600 hover:bg-neutral-900/30 transition-colors text-neutral-400"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}