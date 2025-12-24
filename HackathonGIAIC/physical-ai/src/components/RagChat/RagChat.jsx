import React, { useState, useEffect } from 'react';
import './RagChat.css';
import RagApiService from './api';

/**
 * RagChat Component
 * A floating chat widget that allows users to ask questions to the RAG Agent
 */
const RagChat = ({ backendUrl = 'bqh39ptx.up.railway.app' }) => {
  // Initialize state without localStorage during SSR
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  // Initialize API service
  const apiService = new RagApiService(backendUrl);

  // Load saved state from localStorage only on client-side
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedState = localStorage.getItem('ragChatIsOpen');
      if (savedState) {
        setIsOpen(JSON.parse(savedState));
      }
    }
  }, []);

  const toggleChat = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    // Save state to local storage only on client-side
    if (typeof window !== 'undefined') {
      localStorage.setItem('ragChatIsOpen', JSON.stringify(newState));
    }
  };

  // Validate response format matches expected data model
  const validateResponse = (response) => {
    if (typeof response !== 'object' || response === null) {
      throw new Error('Invalid response format: response is not an object');
    }

    if (response.answer === undefined) {
      console.warn('Response missing answer field');
    }

    if (response.sources === undefined) {
      console.warn('Response missing sources field');
    } else if (!Array.isArray(response.sources)) {
      throw new Error('Invalid response format: sources is not an array');
    }

    if (response.matched_chunks === undefined) {
      console.warn('Response missing matched_chunks field');
    } else if (!Array.isArray(response.matched_chunks)) {
      throw new Error('Invalid response format: matched_chunks is not an array');
    }

    if (Array.isArray(response.matched_chunks)) {
      response.matched_chunks.forEach((chunk, index) => {
        if (typeof chunk !== 'object' || chunk === null) {
          throw new Error(`Invalid response format: chunk at index ${index} is not an object`);
        }
        if (typeof chunk.rank === 'undefined') {
          console.warn(`Chunk at index ${index} missing rank field`);
        }
        if (typeof chunk.text === 'undefined') {
          throw new Error(`Invalid response format: chunk at index ${index} missing text field`);
        }
        if (typeof chunk.source === 'undefined') {
          console.warn(`Chunk at index ${index} missing source field`);
        }
        if (typeof chunk.similarity_score === 'undefined') {
          console.warn(`Chunk at index ${index} missing similarity_score field`);
        }
      });
    }

    return true;
  };

  // Retry function with exponential backoff
  const retryWithBackoff = async (fn, maxRetries = 3, baseDelay = 1000) => {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await fn();
      } catch (error) {
        if (i === maxRetries - 1) {
          throw error;
        }

        if (error.message.includes('Backend error: 4')) {
          throw error;
        }

        const delay = baseDelay * Math.pow(2, i) + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedValue = inputValue.trim();
    if (!trimmedValue) {
      setError('Please enter a question');
      console.log('[RagChat] Input validation failed: empty question');
      return;
    }

    if (trimmedValue.length > 10000) {
      setError('Question is too long. Please limit to 10,000 characters.');
      console.log('[RagChat] Input validation failed: question too long', {
        length: trimmedValue.length,
        limit: 10000
      });
      return;
    }

    if (isSubmitting) {
      console.log('[RagChat] Submission blocked: already submitting');
      return;
    }

    setIsSubmitting(true);
    setIsLoading(true);
    setError(null);
    setResponse(null);

    console.log('[RagChat] Submitting question:', trimmedValue.substring(0, 50) + '...');

    try {
      const apiResponse = await retryWithBackoff(() => apiService.askQuestion(trimmedValue));
      validateResponse(apiResponse);
      setResponse(apiResponse);

      console.log('[RagChat] Received response:', {
        hasAnswer: !!apiResponse.answer,
        sourcesCount: apiResponse.sources?.length || 0,
        chunksCount: apiResponse.matched_chunks?.length || 0
      });
    } catch (err) {
      setError(err.message || 'Failed to get response from RAG Agent');
      console.error('[RagChat] Error submitting question:', err);
    } finally {
      setIsLoading(false);
      setIsSubmitting(false);
      console.log('[RagChat] Submission completed');
    }
  };

  return (
    <div
      className={`rag-chat-widget ${isOpen ? 'open' : 'closed'}`}
      role="complementary"
      aria-label="AI Assistant Chat"
    >
      {!isOpen ? (
        <button
          className="rag-chat-toggle"
          onClick={toggleChat}
          aria-label="Open AI Assistant"
          aria-expanded="false"
        >
          💬
        </button>
      ) : (
        <div
          className="rag-chat-container"
          role="dialog"
          aria-modal="true"
          aria-label="AI Assistant Chat"
        >
          <div className="rag-chat-header" role="banner">
            <span className="rag-chat-title">AI Assistant</span>
            <button
              className="rag-chat-close"
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>

          <div
            className="rag-chat-content"
            role="main"
            aria-live="polite"
            aria-relevant="additions text"
          >
            {response && (
              <div className="rag-response" role="region" aria-labelledby="response-heading">
                {response.answer && (
                  <div className="rag-answer" id="response-heading" role="heading" aria-level="2">
                    <strong>Answer:</strong> {response.answer}
                  </div>
                )}
                {response.sources && response.sources.length > 0 && (
                  <div className="rag-sources" role="region" aria-labelledby="sources-heading">
                    <strong id="sources-heading">📚 Sources:</strong>
                    <ul>
                      {response.sources.map((source, index) => (
                        <li key={index} aria-label={`Source ${index + 1}: ${source}`}>
                          {source}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {response.matched_chunks && response.matched_chunks.length > 0 && (
                  <div className="rag-matched-chunks" role="region" aria-labelledby="chunks-heading">
                    <strong id="chunks-heading">🔗 Reference Chunks:</strong>
                    <div className="chunks-list" role="list">
                      {response.matched_chunks.map((chunk, index) => (
                        <div key={index} className="chunk-item" role="listitem">
                          <div className="chunk-text">
                            <em>{chunk.text.substring(0, 200)}{chunk.text.length > 200 ? '...' : ''}</em>
                          </div>
                          <div className="chunk-meta" aria-label={`Chunk ${index + 1} metadata`}>
                            <span className="chunk-source">📄 {chunk.source}</span>
                            <span className="chunk-score">🎯 {chunk.similarity_score?.toFixed(2)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {response.error && (
                  <div className="rag-backend-error" role="alert">
                    <strong>⚠️ Backend Error:</strong> {response.error}
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="rag-error" role="alert">
                <div className="error-content">
                  <strong>⚠️ Error:</strong> {error}
                </div>
                <button
                  className="retry-button"
                  onClick={() => handleSubmit({ preventDefault: () => {} })}
                  aria-label="Retry the last request"
                >
                  🔄 Retry
                </button>
              </div>
            )}

            {isLoading && (
              <div className="rag-loading" role="status" aria-live="polite">
                <div className="spinner" role="img" aria-label="Loading"></div>
                <span>🤖 Thinking...</span>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="rag-chat-form" role="form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (!isSubmitting && !isLoading) {
                    handleSubmit(e);
                  }
                }
              }}
              placeholder="Ask about Physical AI concepts..."
              className="rag-input"
              disabled={isLoading || isSubmitting}
              aria-label="Type your question here"
              aria-describedby={error ? "error-message" : undefined}
            />
            <button
              type="submit"
              disabled={isLoading || isSubmitting}
              className="rag-submit"
              aria-label="Submit question"
            >
              🚀
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default RagChat;
