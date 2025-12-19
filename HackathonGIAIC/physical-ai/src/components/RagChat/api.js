import axios from 'axios';

/**
 * API service for RAG Agent communication
 */
class RagApiService {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.api = axios.create({
      baseURL: baseURL,
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Ask a question to the RAG Agent
   * @param {string} query - The question to ask
   * @param {number} top_k - Number of chunks to retrieve (default: 5)
   * @param {number} threshold - Similarity score threshold (default: 0.6)
   * @returns {Promise<Object>} Response from the RAG Agent
   */
  async askQuestion(query, top_k = 5, threshold = 0.6) {
    try {
      const response = await this.api.post('/ask', {
        query,
        top_k,
        threshold,
      });
      return response.data;
    } catch (error) {
      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        throw new Error(`Backend error: ${error.response.status} - ${error.response.data?.error || error.response.statusText}`);
      } else if (error.request) {
        // Request was made but no response received
        throw new Error('Network error: Unable to reach the RAG Agent backend');
      } else {
        // Something else happened
        throw new Error(`Request error: ${error.message}`);
      }
    }
  }

  /**
   * Ask a question to the RAG Agent using POST method
   * @param {string} query - The question to ask
   * @param {number} top_k - Number of chunks to retrieve (default: 5)
   * @param {number} threshold - Similarity score threshold (default: 0.6)
   * @returns {Promise<Object>} Response from the RAG Agent
   */
  async askQuestionPost(query, top_k = 5, threshold = 0.6) {
    try {
      const response = await this.api.post('/ask', {
        query,
        top_k,
        threshold,
      });
      return response.data;
    } catch (error) {
      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        throw new Error(`Backend error: ${error.response.status} - ${error.response.data?.error || error.response.statusText}`);
      } else if (error.request) {
        // Request was made but no response received
        throw new Error('Network error: Unable to reach the RAG Agent backend');
      } else {
        // Something else happened
        throw new Error(`Request error: ${error.message}`);
      }
    }
  }

  /**
   * Check if the backend service is healthy
   * @returns {Promise<Object>} Health check response
   */
  async healthCheck() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`Health check failed: ${error.message}`);
    }
  }
}

export default RagApiService;