import React, { useState } from 'react';
import './RagChat.css';
import RagApiService from './api';

/**
 * RagChat Component
 * A floating chat widget that allows users to ask questions to the RAG Agent
 */
const RagChat = ({ backendUrl = 'http://localhost:8000' }) => {
  // Initialize state with value from local storage if available
  const [isOpen, setIsOpen] = useState(() => {
    const savedState = localStorage.getItem('ragChatIsOpen');
    return savedState ? JSON.parse(savedState) : false;
  });

  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false); // Submission lock
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  // Initialize API service
  const apiService = new RagApiService(backendUrl);

  const toggleChat = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    // Save state to local storage
    localStorage.setItem('ragChatIsOpen', JSON.stringify(newState));
  };

  // Validate response format matches expected data model
  const validateResponse = (response) => {
    // Check if response has required fields
    if (typeof response !== 'object' || response === null) {
      throw new Error('Invalid response format: response is not an object');
    }

    // Check answer field
    if (response.answer === undefined) {
      console.warn('Response missing answer field');
    }

    // Check sources field
    if (response.sources === undefined) {
      console.warn('Response missing sources field');
    } else if (!Array.isArray(response.sources)) {
      throw new Error('Invalid response format: sources is not an array');
    }

    // Check matched_chunks field
    if (response.matched_chunks === undefined) {
      console.warn('Response missing matched_chunks field');
    } else if (!Array.isArray(response.matched_chunks)) {
      throw new Error('Invalid response format: matched_chunks is not an array');
    }

    // Validate each chunk if present
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
          // Last attempt, throw the error
          throw error;
        }

        // Check if it's a client error (4xx) that shouldn't be retried
        if (error.message.includes('Backend error: 4')) {
          throw error; // Don't retry client errors
        }

        // Calculate delay with exponential backoff and jitter
        const delay = baseDelay * Math.pow(2, i) + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Input validation
    const trimmedValue = inputValue.trim();
    if (!trimmedValue) {
      setError('Please enter a question');
      // Log for debugging
      console.log('[RagChat] Input validation failed: empty question');
      return;
    }

    // Check for maximum length
    if (trimmedValue.length > 10000) {
      setError('Question is too long. Please limit to 10,000 characters.');
      // Log for debugging
      console.log('[RagChat] Input validation failed: question too long', {
        length: trimmedValue.length,
        limit: 10000
      });
      return;
    }

    // Check if already submitting to prevent concurrent requests
    if (isSubmitting) {
      // Log for debugging
      console.log('[RagChat] Submission blocked: already submitting');
      return; // Ignore the submission if already processing
    }

    setIsSubmitting(true);
    setIsLoading(true);
    setError(null);
    setResponse(null);

    // Log submission start for debugging
    console.log('[RagChat] Submitting question:', trimmedValue.substring(0, 50) + '...');

    try {
      // Call the backend API to ask the question with retry logic
      const apiResponse = await retryWithBackoff(() => apiService.askQuestion(trimmedValue));

      // Validate the response format
      validateResponse(apiResponse);

      setResponse(apiResponse);

      // Log successful response for debugging
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
      setIsSubmitting(false); // Release the submission lock

      // Log completion for debugging
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
          💬 Ask AI
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
                    <strong id="sources-heading">Sources:</strong>
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
                    <strong id="chunks-heading">Reference Chunks:</strong>
                    <div className="chunks-list" role="list">
                      {response.matched_chunks.map((chunk, index) => (
                        <div key={index} className="chunk-item" role="listitem">
                          <div className="chunk-text">
                            <em>{chunk.text.substring(0, 200)}{chunk.text.length > 200 ? '...' : ''}</em>
                          </div>
                          <div className="chunk-meta" aria-label={`Chunk ${index + 1} metadata`}>
                            <span className="chunk-source">Source: {chunk.source}</span>
                            <span className="chunk-score">Score: {chunk.similarity_score?.toFixed(2)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {response.error && (
                  <div className="rag-backend-error" role="alert">
                    <strong>Backend Error:</strong> {response.error}
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="rag-error" role="alert">
                <div className="error-content">
                  <strong>Error:</strong> {error}
                </div>
                <button
                  className="retry-button"
                  onClick={() => handleSubmit({ preventDefault: () => {} })}
                  aria-label="Retry the last request"
                >
                  Retry
                </button>
              </div>
            )}

            {isLoading && (
              <div className="rag-loading" role="status" aria-live="polite">
                <div className="spinner" role="img" aria-label="Loading"></div>
                <span>Processing your question...</span>
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
              placeholder="Ask a question..."
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
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default RagChat;