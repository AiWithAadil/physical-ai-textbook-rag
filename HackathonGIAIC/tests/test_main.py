import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from backend.main import (
    get_all_urls, extract_text_from_url, chunk_text,
    embed, create_collection, save_chunk_to_qdrant, url_hash
)


class TestUrlHash:
    def test_url_hash_generation(self):
        url = "https://example.com"
        result = url_hash(url)
        assert isinstance(result, str)
        assert len(result) == 12  # First 12 chars of MD5 hash


class TestGetAllUrls:
    @patch('requests.get')
    @patch('bs4.BeautifulSoup')
    def test_get_all_urls_success(self, mock_bs, mock_get):
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body><a href="/page1">Page 1</a></body></html>'
        mock_get.return_value = mock_response

        mock_soup = Mock()
        mock_soup.find_all.return_value = [Mock()]
        mock_soup.find_all.return_value[0].get = Mock(return_value="/page1")
        mock_bs.return_value = mock_soup

        result = get_all_urls("https://example.com", max_depth=1)
        assert isinstance(result, list)


class TestExtractTextFromUrl:
    @patch('requests.get')
    @patch('bs4.BeautifulSoup')
    def test_extract_text_from_url_success(self, mock_bs, mock_get):
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><head><title>Test</title></head><body><p>Test content</p></body></html>'
        mock_get.return_value = mock_response

        mock_title = Mock()
        mock_title.get_text.return_value = "Test"

        mock_body = Mock()
        mock_body.get_text.return_value = "Test content"

        mock_soup = Mock()
        mock_soup.find.side_effect = lambda x: mock_title if x == 'title' else mock_body
        mock_bs.return_value = mock_soup

        text, title = extract_text_from_url("https://example.com")
        assert title == "Test"
        assert "Test content" in text


class TestChunkText:
    def test_chunk_text_basic(self):
        text = "This is a test sentence. This is another sentence. And a third one."
        chunks = chunk_text(text, chunk_size=30, overlap=5)

        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all('position' in chunk for chunk in chunks)

    def test_chunk_text_empty(self):
        chunks = chunk_text("")
        assert chunks == []

    def test_chunk_text_single_chunk(self):
        text = "Short text"
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0]['content'] == text


class TestEmbed:
    @patch.dict(os.environ, {"COHERE_API_KEY": "test-key"})
    def test_embed_empty_list(self):
        result = embed([])
        assert result == []

    @patch('cohere.Client')
    def test_embed_with_mock_client(self, mock_cohere):
        # Mock the Cohere client
        mock_embed_response = Mock()
        mock_embed_response.embeddings = [[0.1, 0.2, 0.3]]

        mock_client_instance = Mock()
        mock_client_instance.embed.return_value = mock_embed_response
        mock_cohere.return_value = mock_client_instance

        result = embed(["test text"])

        assert len(result) == 1
        assert result[0]['embedding'] == [0.1, 0.2, 0.3]


class TestCreateCollection:
    @patch('qdrant_client.QdrantClient')
    def test_create_collection(self, mock_qdrant_client):
        mock_client = Mock()
        mock_collections = Mock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_qdrant_client.return_value = mock_client

        result = create_collection("test_collection")

        assert result is True
        mock_client.create_collection.assert_called_once()


class TestSaveChunkToQdrant:
    @patch('qdrant_client.QdrantClient')
    def test_save_chunk_to_qdrant(self, mock_qdrant_client):
        mock_client = Mock()
        mock_qdrant_client.return_value = mock_client

        result = save_chunk_to_qdrant(
            chunk_id="test_id",
            embedding=[0.1, 0.2, 0.3],
            content="test content",
            source_url="https://example.com",
            title="Test Title",
            position=0
        )

        assert result is True
        mock_client.upsert.assert_called_once()