import React, { useState, useEffect } from 'react';
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

interface Play {
  title: string;
  category: string;
}

export default function Home() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedPlay, setSelectedPlay] = useState<Play | null>(null);
  const [showTragediesOnly, setShowTragediesOnly] = useState(false);
  const [activeTab, setActiveTab] = useState<'short' | 'detailed'>('short');

  const backendUrl = typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000') : 'http://localhost:8000';

  // Shakespeare plays data
  const plays: Play[] = [
    { title: "All's Well That Ends Well", category: "Comedy" },
    { title: "Antony and Cleopatra", category: "Tragedy" },
    { title: "As You Like It", category: "Comedy" },
    { title: "The Comedy of Errors", category: "Comedy" },
    { title: "Coriolanus", category: "Tragedy" },
    { title: "Cymbeline", category: "Tragedy" },
    { title: "Hamlet", category: "Tragedy" },
    { title: "Henry IV, Part 1", category: "History" },
    { title: "Henry IV, Part 2", category: "History" },
    { title: "Henry V", category: "History" },
    { title: "Henry VI, Part 1", category: "History" },
    { title: "Henry VI, Part 2", category: "History" },
    { title: "Henry VI, Part 3", category: "History" },
    { title: "Henry VIII", category: "History" },
    { title: "Julius Caesar", category: "Tragedy" },
    { title: "King John", category: "History" },
    { title: "King Lear", category: "Tragedy" },
    { title: "Love's Labour's Lost", category: "Comedy" },
    { title: "Macbeth", category: "Tragedy" },
    { title: "Measure for Measure", category: "Comedy" },
    { title: "The Merchant of Venice", category: "Comedy" },
    { title: "The Merry Wives of Windsor", category: "Comedy" },
    { title: "A Midsummer Night's Dream", category: "Comedy" },
    { title: "Much Ado About Nothing", category: "Comedy" },
    { title: "Othello", category: "Tragedy" },
    { title: "Pericles, Prince of Tyre", category: "Tragedy" },
    { title: "Richard II", category: "History" },
    { title: "Richard III", category: "History" },
    { title: "Romeo and Juliet", category: "Tragedy" },
    { title: "The Taming of the Shrew", category: "Comedy" },
    { title: "The Tempest", category: "Comedy" },
    { title: "Timon of Athens", category: "Tragedy" },
    { title: "Titus Andronicus", category: "Tragedy" },
    { title: "Troilus and Cressida", category: "Tragedy" },
    { title: "Twelfth Night", category: "Comedy" },
    { title: "The Two Gentlemen of Verona", category: "Comedy" },
    { title: "The Two Noble Kinsmen", category: "Tragedy" },
    { title: "The Winter's Tale", category: "Comedy" }
  ];

  const filteredPlays = showTragediesOnly 
    ? plays.filter(play => play.category === 'Tragedy')
    : plays;

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError('');
    setAnswer('');
    setSources([]);

    try {
      const requestPayload: any = {
        question: question,
        k: 5 // Now requests 5 chunks
      };

      // Add play filter if a play is selected
      if (selectedPlay) {
        requestPayload.filters = {
          play: selectedPlay.title
        };
      }

      const response = await axios.post(`${backendUrl}/answer`, requestPayload);
      const data: AnswerResponse = response.data;
      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred while processing your question.');
    } finally {
      setLoading(false);
    }
  };

  const selectPlay = (play: Play) => {
    setSelectedPlay(play);
  };

  return (
    <>
      <Head>
        <title>Shakespeare GPT - Academic Dictionary Style</title>
        <meta name="description" content="Ask questions about Shakespeare and get contextual answers from his plays" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="min-h-screen" style={{ backgroundColor: '#E3D9C9', fontFamily: 'Inter, sans-serif' }}>
        <div className="flex h-screen">
          {/* Sidebar */}
          <div className="w-80 bg-white shadow-lg overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold" style={{ color: '#43B3AE' }}>SHAKESPEARE GPT</h2>
              <p className="text-sm text-gray-600 mt-1">Academic Dictionary Style</p>
            </div>

            {/* Filter Toggle */}
            <div className="p-4 border-b border-gray-200">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showTragediesOnly}
                  onChange={(e) => setShowTragediesOnly(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm" style={{ color: '#43B3AE' }}>Show Tragedies Only</span>
              </label>
            </div>

            {/* Plays List */}
            <div className="p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Plays</h3>
              <div className="space-y-1">
                {filteredPlays.map((play, index) => (
                  <div
                    key={index}
                    onClick={() => selectPlay(play)}
                    className={`px-3 py-2 rounded text-sm cursor-pointer transition-all duration-200 ${
                      selectedPlay?.title === play.title 
                        ? 'text-white' 
                        : 'hover:bg-gray-100'
                    }`}
                    style={{
                      backgroundColor: selectedPlay?.title === play.title ? '#B34348' : 'transparent',
                      color: selectedPlay?.title === play.title ? 'white' : '#43B3AE'
                    }}
                  >
                    <div className="font-medium">{play.title}</div>
                    <div className="text-xs text-gray-500">{play.category}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 bg-white">
              <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold" style={{ color: '#43B3AE', fontFamily: "'Crimson Text', serif" }}>
                  Shakespeare GPT
                </h1>
                <p className="text-gray-600 mt-1">Ask questions about Shakespeare's works</p>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="max-w-4xl mx-auto">
                {/* Info Bar */}
                <div className="bg-white rounded-lg p-4 mb-6 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#B34348' }}></div>
                    <span className="text-sm text-gray-600">
                      {selectedPlay 
                        ? `Searching within: ${selectedPlay.title} (${selectedPlay.category})`
                        : 'Searching across all Shakespeare plays'
                      }
                    </span>
                  </div>
                </div>

                {/* Search Input - Centered */}
                <div className="mb-8">
                  <div className="max-w-2xl mx-auto">
                    <div className="flex gap-3">
                      <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder={selectedPlay ? `Ask about ${selectedPlay.title}...` : "Ask about Shakespeare's plays, characters, or themes..."}
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        style={{ backgroundColor: '#f7fafc' }}
                        onKeyPress={(e) => e.key === 'Enter' && askQuestion()}
                      />
                      <button
                        onClick={askQuestion}
                        disabled={loading || !question.trim()}
                        className="px-6 py-3 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
                        style={{ backgroundColor: '#B34348' }}
                      >
                        {loading ? '🤔 Thinking...' : 'Send'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="max-w-2xl mx-auto mb-6">
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                      ❌ {error}
                    </div>
                  </div>
                )}

                {/* Answer Section */}
                {answer && (
                  <div className="max-w-4xl mx-auto">
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                      {/* Question Display */}
                      <div className="p-6 border-b border-gray-200">
                        <h3 className="text-lg font-semibold" style={{ color: '#43B3AE' }}>
                          Question
                        </h3>
                        <p className="text-gray-700 mt-2">{question}</p>
                      </div>

                      {/* Answer Tabs */}
                      <div className="border-b border-gray-200">
                        <div className="flex">
                          <button
                            onClick={() => setActiveTab('short')}
                            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                              activeTab === 'short' 
                                ? 'border-blue-500 text-blue-600' 
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                          >
                            Short Answer
                          </button>
                          <button
                            onClick={() => setActiveTab('detailed')}
                            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                              activeTab === 'detailed' 
                                ? 'border-blue-500 text-blue-600' 
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                          >
                            Detailed Answer
                          </button>
                        </div>
                      </div>

                      {/* Answer Content */}
                      <div className="p-6">
                        <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                          {activeTab === 'short' ? (
                            <div>
                              {selectedPlay 
                                ? `Shakespeare's exploration of this theme in ${selectedPlay.title} demonstrates his characteristic depth and complexity within this specific work.`
                                : "Shakespeare's exploration of this theme appears across multiple plays, with particular emphasis in the tragedies and comedies."
                              }
                            </div>
                          ) : (
                            <div>
                              {selectedPlay 
                                ? `In ${selectedPlay.title}, Shakespeare's treatment of this subject matter is particularly noteworthy. This ${selectedPlay.category.toLowerCase()} showcases the Bard's mastery of character development and thematic exploration.

The play's unique approach to this theme reveals Shakespeare's understanding of human nature and dramatic structure. Through the lens of ${selectedPlay.title}, we can see how the playwright weaves complex narratives that resonate with audiences across centuries.

The character dynamics and plot developments in this work provide rich material for analysis, demonstrating Shakespeare's ability to create compelling drama that explores universal themes while remaining deeply personal and emotionally resonant.`
                                : `Shakespeare's treatment of this subject matter demonstrates his characteristic depth and complexity. In the tragedies, we see this theme explored through the lens of human suffering and moral ambiguity, while in the comedies, it often serves as a vehicle for social commentary and romantic resolution.

The most notable examples can be found in Hamlet, where the protagonist's soliloquies reveal deep philosophical contemplation, and in A Midsummer Night's Dream, where the theme is treated with characteristic wit and whimsy. These contrasting approaches highlight Shakespeare's remarkable range as a dramatist.

Further examination of the historical plays reveals how this theme intersects with questions of power, legitimacy, and the nature of kingship. The character development across these works shows Shakespeare's evolving understanding of human psychology and motivation.`
                              }
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Sources */}
                {sources.length > 0 && (
                  <div className="max-w-4xl mx-auto mt-6">
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h3 className="text-lg font-semibold mb-4" style={{ color: '#43B3AE' }}>
                        📚 Sources
                      </h3>
                      <div className="space-y-3">
                        {sources.map((source, index) => (
                          <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-semibold text-gray-800">
                                  {source.play} - {source.act}
                                </h4>
                                <p className="text-gray-600 text-sm mt-1">
                                  {source.scene_title}
                                </p>
                              </div>
                              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                {source.similarity}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>


      </main>
    </>
  );
} 