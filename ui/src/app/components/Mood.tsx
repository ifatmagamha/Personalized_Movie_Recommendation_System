import { useState, useRef } from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, Mic, MicOff, Send } from 'lucide-react';

interface MoodInputScreenProps {
  onBack: () => void;
  onSubmit: (text: string) => void;
}

export function MoodInputScreen({ onBack, onSubmit }: MoodInputScreenProps) {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleVoice = () => {
    setIsListening(!isListening);
    // Mock voice input
    if (!isListening) {
      setTimeout(() => {
        setInput("feeling kind of lost and restless, want something quiet but not boring");
        setIsListening(false);
      }, 2000);
    }
  };

  const handleSubmit = () => {
    if (input.trim()) {
      onSubmit(input.trim());
    }
  };

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 relative overflow-hidden">
      {/* Neon accents */}
      <div className="absolute top-1/4 left-0 w-64 h-64 bg-pink-500/15 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-1/4 right-0 w-64 h-64 bg-blue-500/15 rounded-full blur-[120px] animate-pulse" 
           style={{ animationDelay: '1.5s' }} />
      
      {/* Grain */}
      <div className="fixed inset-0 opacity-[0.03] pointer-events-none bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIiB4PSIwIiB5PSIwIj48ZmVUdXJidWxlbmNlIGJhc2VGcmVxdWVuY3k9Ii43NSIgc3RpdGNoVGlsZXM9InN0aXRjaCIgdHlwZT0iZnJhY3RhbE5vaXNlIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxwYXRoIGQ9Ik0wIDBoMzAwdjMwMEgweiIgZmlsdGVyPSJ1cmwoI2EpIiBvcGFjaXR5PSIuMDUiLz48L3N2Zz4=')]" />

      {/* Header */}
      <div className="relative border-b border-stone-900 bg-stone-950/80 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-stone-400 hover:text-stone-200 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">back</span>
          </button>
        </div>
      </div>

      <div className="relative container mx-auto px-6 py-16 max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 text-center"
        >
          <h2 className="mb-4">how are you feeling?</h2>
          <p className="text-stone-400 text-sm">
            describe your mood, we'll find something that fits
          </p>
        </motion.div>

        {/* Input Area */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="relative bg-stone-900/50 border border-stone-800 p-6 mb-8"
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="i'm feeling..."
            className="w-full bg-transparent border-none outline-none resize-none text-stone-200 placeholder:text-stone-700 min-h-[150px]"
            style={{ fontFamily: 'monospace' }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.metaKey) {
                handleSubmit();
              }
            }}
          />

          {/* Bottom Bar */}
          <div className="flex items-center justify-between pt-4 border-t border-stone-900">
            <button
              onClick={handleVoice}
              className={`flex items-center gap-2 px-4 py-2 border transition-all ${
                isListening
                  ? 'border-pink-500/50 bg-pink-500/10 text-pink-400'
                  : 'border-stone-800 hover:border-stone-700 text-stone-400'
              }`}
            >
              {isListening ? (
                <>
                  <MicOff className="w-4 h-4" />
                  <span className="text-sm">listening...</span>
                </>
              ) : (
                <>
                  <Mic className="w-4 h-4" />
                  <span className="text-sm">use voice</span>
                </>
              )}
            </button>

            <button
              onClick={handleSubmit}
              disabled={!input.trim()}
              className={`flex items-center gap-2 px-6 py-2 transition-all ${
                input.trim()
                  ? 'bg-gradient-to-r from-pink-500/20 to-blue-500/20 border border-pink-500/40 hover:border-pink-500/60'
                  : 'border border-stone-900 text-stone-700 cursor-not-allowed'
              }`}
            >
              <span className="text-sm">find movies</span>
              <Send className="w-4 h-4" />
            </button>
          </div>
        </motion.div>

        {/* Examples */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <p className="text-xs text-stone-600 uppercase tracking-widest mb-4">
            or try these
          </p>
          <div className="space-y-2">
            {[
              "feeling melancholic, want something slow and beautiful",
              "restless energy, need something tense but not scary",
              "lonely 3am vibes, something quiet and contemplative",
            ].map((example) => (
              <button
                key={example}
                onClick={() => setInput(example)}
                className="w-full text-left px-4 py-3 border border-stone-900 hover:border-stone-700 hover:bg-stone-900/30 transition-all text-sm text-stone-500 hover:text-stone-300"
              >
                "{example}"
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
