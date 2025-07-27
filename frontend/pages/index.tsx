import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Head from 'next/head';

// Updated for Vercel deployment compatibility - v2.0

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

  const backendUrl = 'https://web-production-9f2fc.up.railway.app';

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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
        <script src="https://cdn.tailwindcss.com"></script>
        <style dangerouslySetInnerHTML={{
          __html: `
            body {
              font-family: 'Inter', sans-serif;
              background-color: #E3D9C9;
              margin: 0;
              padding: 0;
            }
            .serif-font {
              font-family: 'Crimson Text', serif;
            }
            .accent-color {
              color: #B34348;
            }
            .accent-bg {
              background-color: #B34348;
            }
            .accent-border {
              border-color: #B34348;
            }
            .main-bg {
              background-color: #E3D9C9;
            }
            .sidebar-bg {
              background-color: #f7fafc;
            }
            .text-dark {
              color: #43B3AE;
            }
            .text-muted {
              color: #718096;
            }
            .play-item {
              cursor: pointer;
              transition: all 0.2s ease;
            }
            .play-item:hover {
              background-color: #E3D9C9;
            }
            .play-item.active {
              background-color: #B34348;
              color: white;
            }
            .search-input {
              background-color: #f7fafc;
              border: 1px solid #E3D9C9;
            }
            .search-input:focus {
              border-color: #B34348;
              box-shadow: 0 0 0 3px rgba(179, 67, 72, 0.1);
            }
            .tab-button {
              transition: all 0.2s ease;
            }
            .tab-button.active {
              border-bottom: 2px solid #B34348;
              color: #B34348;
            }
          `
        }} />
      </Head>

      <main style={{ backgroundColor: '#E3D9C9', fontFamily: 'Inter, sans-serif', minHeight: '100vh' }}>
        <div style={{ display: 'flex', height: '100vh' }}>
          {/* Sidebar */}
          <div style={{ width: '320px', backgroundColor: 'white', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', overflowY: 'auto' }}>
            {/* Filter Toggle */}
            <div style={{ padding: '16px', borderBottom: '1px solid #e2e8f0' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={showTragediesOnly}
                  onChange={(e) => setShowTragediesOnly(e.target.checked)}
                  style={{ borderRadius: '4px' }}
                />
                <span style={{ fontSize: '14px', color: '#43B3AE' }}>Show Tragedies Only</span>
              </label>
            </div>

            {/* Selected Play Display */}
            {selectedPlay && (
              <div style={{ padding: '16px', borderBottom: '1px solid #e2e8f0', backgroundColor: '#f8f9fa' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#43B3AE' }}>Selected Play:</div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>{selectedPlay.title}</div>
                  </div>
                  <button
                    onClick={() => setSelectedPlay(null)}
                    style={{
                      padding: '4px 8px',
                      fontSize: '12px',
                      backgroundColor: '#B34348',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#a03a3f'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#B34348'}
                  >
                    Deselect
                  </button>
                </div>
              </div>
            )}

            {/* Plays List */}
            <div style={{ padding: '16px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '12px' }}>Plays</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {filteredPlays.map((play, index) => (
                  <div
                    key={index}
                    onClick={() => selectPlay(play)}
                    style={{
                      padding: '8px 12px',
                      borderRadius: '4px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      backgroundColor: selectedPlay?.title === play.title ? '#B34348' : 'transparent',
                      color: selectedPlay?.title === play.title ? 'white' : '#43B3AE'
                    }}
                    onMouseEnter={(e) => {
                      if (selectedPlay?.title !== play.title) {
                        e.currentTarget.style.backgroundColor = '#E3D9C9';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (selectedPlay?.title !== play.title) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                  >
                    <div style={{ fontWeight: '500' }}>{play.title}</div>
                    <div style={{ fontSize: '12px', color: selectedPlay?.title === play.title ? 'rgba(255,255,255,0.7)' : '#6b7280' }}>{play.category}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <div style={{ padding: '24px', borderBottom: '1px solid #e2e8f0', backgroundColor: 'white' }}>
              <div style={{ maxWidth: '1024px', margin: '0 auto' }}>
                <h1 style={{ fontSize: '30px', fontWeight: '700', color: '#43B3AE', margin: 0, fontFamily: 'Crimson Text, serif' }}>
                  Shakespeare GPT
                </h1>
                <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Ask questions about Shakespeare's works</p>
              </div>
            </div>

            {/* Main Content Area */}
            <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
              <div style={{ maxWidth: '1024px', margin: '0 auto' }}>
                {/* Info Bar */}
                <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '16px', marginBottom: '24px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#B34348' }}></div>
                      <span style={{ fontSize: '14px', color: '#6b7280' }}>
                        {selectedPlay 
                          ? `Searching within: ${selectedPlay.title} (${selectedPlay.category})`
                          : 'Searching across all Shakespeare plays'
                        }
                      </span>
                    </div>
                    {selectedPlay && (
                      <button
                        onClick={() => setSelectedPlay(null)}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          backgroundColor: 'transparent',
                          color: '#B34348',
                          border: '1px solid #B34348',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#B34348';
                          e.currentTarget.style.color = 'white';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent';
                          e.currentTarget.style.color = '#B34348';
                        }}
                      >
                        Clear Filter
                      </button>
                    )}
                  </div>
                </div>

                {/* Search Input - Centered */}
                <div style={{ marginBottom: '32px' }}>
                  <div style={{ maxWidth: '512px', margin: '0 auto' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder={selectedPlay ? `Ask about ${selectedPlay.title}...` : "Ask about Shakespeare's plays, characters, or themes..."}
                        style={{
                          flex: 1,
                          padding: '12px 16px',
                          border: '1px solid #d1d5db',
                          borderRadius: '8px',
                          fontSize: '16px',
                          backgroundColor: '#f7fafc',
                          outline: 'none'
                        }}
                        onFocus={(e) => {
                          e.target.style.borderColor = '#B34348';
                          e.target.style.boxShadow = '0 0 0 3px rgba(179, 67, 72, 0.1)';
                        }}
                        onBlur={(e) => {
                          e.target.style.borderColor = '#d1d5db';
                          e.target.style.boxShadow = 'none';
                        }}
                        onKeyPress={(e) => e.key === 'Enter' && askQuestion()}
                      />
                      <button
                        onClick={askQuestion}
                        disabled={loading || !question.trim()}
                        style={{
                          padding: '12px 24px',
                          color: 'white',
                          fontWeight: '600',
                          borderRadius: '8px',
                          transition: 'all 0.2s ease',
                          backgroundColor: '#B34348',
                          border: 'none',
                          cursor: loading || !question.trim() ? 'not-allowed' : 'pointer',
                          opacity: loading || !question.trim() ? 0.5 : 1
                        }}
                      >
                        {loading ? '🤔 Thinking...' : 'Send'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <div style={{ maxWidth: '512px', margin: '0 auto 24px auto' }}>
                    <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', padding: '12px 16px', borderRadius: '8px' }}>
                      ❌ {error}
                    </div>
                  </div>
                )}

                {/* Answer Section */}
                {answer && (
                  <div style={{ maxWidth: '1024px', margin: '0 auto' }}>
                    <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb' }}>
                      {/* Question Display */}
                      <div style={{ padding: '24px', borderBottom: '1px solid #e5e7eb' }}>
                        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#43B3AE', margin: '0 0 8px 0' }}>
                          Question
                        </h3>
                        <p style={{ color: '#374151', margin: 0 }}>{question}</p>
                      </div>



                      {/* Answer Content */}
                      <div style={{ padding: '24px' }}>
                        <div style={{ color: '#374151', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                          {answer}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Sources */}
                {sources.length > 0 && (
                  <div style={{ maxWidth: '1024px', margin: '24px auto 0 auto' }}>
                    <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb', padding: '24px' }}>
                      <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#43B3AE', margin: '0 0 16px 0' }}>
                        📚 Sources
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {sources.map((source, index) => (
                          <div key={index} style={{ backgroundColor: '#f9fafb', borderRadius: '8px', padding: '16px', border: '1px solid #e5e7eb' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                              <div>
                                <h4 style={{ fontWeight: '600', color: '#1f2937', margin: '0 0 4px 0' }}>
                                  {source.play} - {source.act}
                                </h4>
                                <p style={{ color: '#6b7280', fontSize: '14px', margin: 0 }}>
                                  {source.scene_title}
                                </p>
                              </div>
                              <span style={{ fontSize: '12px', backgroundColor: '#dbeafe', color: '#1e40af', padding: '4px 8px', borderRadius: '4px' }}>
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