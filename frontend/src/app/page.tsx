'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (overrideInput?: string) => {
    const text = overrideInput || input;
    if (!text.trim()) return;

    // Add user message immediately
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text }),
      });

      if (!res.ok) throw new Error('Failed to fetch response');
      const data = await res.json();

      let answerText = data.answer;
      if (data.sources && data.sources.length > 0) {
        answerText += '\n\n**Sources:**\n' + data.sources.map((s: string) => `- [${s}](${s})`).join('\n');
      }

      setMessages((prev) => [...prev, { role: 'assistant', content: answerText }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'An error occurred while fetching the response.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4 font-sans">
      <div className="w-full max-w-3xl bg-white shadow-xl rounded-2xl overflow-hidden flex flex-col h-[85vh]">
        {/* Header */}
        <div className="bg-blue-600 text-white py-6 px-6 text-center">
          <h1 className="text-2xl font-bold flex items-center justify-center gap-2">
            📈 Mutual Fund FAQ Assistant
          </h1>
        </div>

        {/* Disclaimer */}
        <div className="bg-red-50 border-b border-red-100 p-3 text-center text-red-600 font-semibold text-sm">
          ⚠️ Facts-only. No investment advice. This tool only provides objective data based on official Groww sources.
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full space-y-6 opacity-70">
              <p className="text-gray-500 text-lg">Ask a question about mutual funds...</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
                {['What is the expense ratio of HDFC Small Cap?', 'Who is the manager for the Mid Cap fund?', 'Should I invest in gold right now?'].map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="p-3 bg-gray-100 hover:bg-blue-50 text-gray-700 hover:text-blue-600 rounded-lg text-sm text-left transition-colors border border-gray-200"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-gray-100 text-gray-800 rounded-bl-none prose prose-sm'
                  }`}
                >
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-500 rounded-2xl rounded-bl-none px-5 py-3 flex gap-2 items-center">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask a question about mutual funds..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
              disabled={isLoading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-full font-medium transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
