import { useState } from 'react';
import axios from 'axios';
import Head from 'next/head';

interface Source {
  index: number;
  play: string;
  act: string;
  scene_title: string;
  similarity: number;
}

interface AnswerResponse {
  answer: string;
  sources: Source[];
}

export default function Home() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError('');
    setAnswer('');
    setSources([]);

    try {
      const response = await axios.post(`${backendUrl}/answer`, {
        question: question,
        k: 3
      });

      const data: AnswerResponse = response.data;
      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred while processing your question.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>ShakespeareGPT - Your AI Shakespeare Guide</title>
        <meta name="description" content="Ask questions about Shakespeare and get contextual answers from his plays" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-white mb-4">
              🎭 ShakespeareGPT
            </h1>
            <p className="text-xl text-purple-200">
              Your AI guide to Shakespeare's works
            </p>
          </div>

          {/* Question Input */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="flex gap-4">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask about Shakespeare's plays, characters, or themes..."
                  className="flex-1 px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  onKeyPress={(e) => e.key === 'Enter' && askQuestion()}
                />
                <button
                  onClick={askQuestion}
                  disabled={loading || !question.trim()}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white font-semibold rounded-lg transition-colors"
                >
                  {loading ? '🤔 Thinking...' : 'Ask'}
                </button>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="max-w-4xl mx-auto mb-8">
              <div className="bg-red-500/20 border border-red-400 text-red-200 px-4 py-3 rounded-lg">
                ❌ {error}
              </div>
            </div>
          )}

          {/* Answer */}
          {answer && (
            <div className="max-w-4xl mx-auto mb-8">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                <h2 className="text-2xl font-semibold text-white mb-4">💡 Answer</h2>
                <div className="text-purple-100 leading-relaxed whitespace-pre-wrap">
                  {answer}
                </div>
              </div>
            </div>
          )}

          {/* Sources */}
          {sources.length > 0 && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                <h2 className="text-2xl font-semibold text-white mb-4">📚 Sources</h2>
                <div className="space-y-3">
                  {sources.map((source, index) => (
                    <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-purple-200">
                            {source.play} - {source.act}
                          </h3>
                          <p className="text-purple-100 text-sm mt-1">
                            {source.scene_title}
                          </p>
                        </div>
                        <span className="text-xs bg-purple-600 text-white px-2 py-1 rounded">
                          {source.similarity}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="text-center mt-12 text-purple-200">
            <p>Powered by OpenAI GPT and ChromaDB</p>
          </div>
        </div>
      </main>
    </>
  );
} 