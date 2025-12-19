# Tasks: Retrieval + Pipeline Testing for RAG Ingestion

**Input**: Design documents from `/specs/3-retrieval-testing/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/retrieval-api.openapi.yaml

**Tests**: Optional - include unit, integration, and contract tests for comprehensive coverage

**Organization**: Tasks are grouped by user story (US1-US4) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4)
- **File paths**: All in `backend/` per implementation plan

---

## Implementation Strategy

**MVP Scope**: User Story 1 (Query and retrieve top-k matches) + foundational services
**Phase 2**: Add data verification (US2) for integrity checking
**Phase 3**: Add metadata handling (US3) for complete traceability
**Phase 4**: Add end-to-end JSON pipeline (US4) for testing

**Parallel Opportunities**:
- Models can be created in parallel (T005-T008)
- Utility modules can be created in parallel (T010-T011)
- Services depend on models but can be parallelized per service

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan in `backend/` directory
- [ ] T002 Initialize Python 3.11 project with dependencies in `backend/requirements.txt`
- [ ] T003 [P] Configure pytest and pytest-asyncio in `backend/pytest.ini`
- [ ] T004 [P] Create environment configuration loader in `backend/src/config.py`
- [ ] T005 [P] Create `.env.example` template file in `backend/` with required variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work begins until this phase is complete

### Data Models (Foundational - all stories depend on these)

- [ ] T006 [P] Create SearchQuery model with validation in `backend/src/models/search_query.py`
- [ ] T007 [P] Create ChunkMetadata model in `backend/src/models/metadata.py`
- [ ] T008 [P] Create SearchResult model with invariants in `backend/src/models/search_result.py`
- [ ] T009 [P] Create RetrievalResponse envelope model in `backend/src/models/response.py`

### Utilities (Foundational - all stories depend on these)

- [ ] T010 [P] Create error handling utilities in `backend/src/utils/error_handler.py`
- [ ] T011 [P] Create JSON formatting utilities in `backend/src/utils/json_formatter.py`
- [ ] T012 [P] Create validation utilities for query parameters in `backend/src/utils/validators.py`

### External Service Clients (Foundational)

- [ ] T013 Create AsyncQdrantClient wrapper in `backend/src/services/qdrant_client.py` with async connection pooling
- [ ] T014 Create EmbeddingServiceClient for Cohere in `backend/src/services/embedding_service.py`

### Logging and Configuration

- [ ] T015 Setup structured logging in `backend/src/config.py` with debug/info/error levels
- [ ] T016 Create exception hierarchy in `backend/src/utils/exceptions.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Query Vectors and Retrieve Top-K Matches (Priority: P1) 🎯 MVP

**Goal**: Implement semantic search that queries Qdrant for top-k similar document chunks ranked by similarity score

**Independent Test**: Submit a query string to RetrievalService, receive ranked results with similarity scores, verify top results are semantically relevant

### Tests for User Story 1

- [ ] T017 [P] [US1] Unit test RetrievalService initialization in `backend/tests/unit/test_retrieval_service.py`
- [ ] T018 [P] [US1] Unit test query embedding in `backend/tests/unit/test_embedding_service.py`
- [ ] T019 [P] [US1] Unit test Qdrant client connection in `backend/tests/unit/test_qdrant_client.py`
- [ ] T020 [US1] Integration test end-to-end search in `backend/tests/integration/test_end_to_end_retrieval.py` (embed query → search Qdrant → return results)
- [ ] T021 [US1] Contract test response schema validation in `backend/tests/contract/test_response_schema.py`

### Implementation for User Story 1

- [ ] T022 [US1] Implement RetrievalService.search() method in `backend/src/services/retrieval_service.py` to: (1) validate query, (2) embed query with Cohere, (3) search Qdrant, (4) format response
- [ ] T023 [P] [US1] Implement similarity score ranking in `backend/src/services/retrieval_service.py` (ensure results sorted descending by similarity)
- [ ] T024 [P] [US1] Implement top-k filtering in `backend/src/services/retrieval_service.py` (limit results to requested count)
- [ ] T025 [P] [US1] Implement similarity threshold filtering in `backend/src/services/retrieval_service.py` (exclude results below threshold)
- [ ] T026 [US1] Add error handling for empty results and missing embeddings in `backend/src/services/retrieval_service.py`
- [ ] T027 [US1] Add logging for search operations in `backend/src/services/retrieval_service.py` with query, result count, latency

**Parallel Execution Suggestion** (T023-T025 can run in parallel after T022):
```
T022 (main search logic)
  ├── T023 [P] (ranking)
  ├── T024 [P] (top-k)
  └── T025 [P] (threshold)
  └── T026 (error handling - depends on above)
```

**Checkpoint**: User Story 1 complete - semantic search working with ranked results

---

## Phase 4: User Story 2 - Verify Retrieved Chunks Match Original Content (Priority: P1)

**Goal**: Ensure 100% data integrity by verifying retrieved chunks exactly match original extracted text

**Independent Test**: Compare retrieved chunks against original source text, verify exact byte-for-byte matches, identify any truncation or corruption

### Tests for User Story 2

- [ ] T028 [P] [US2] Unit test ValidationService in `backend/tests/unit/test_validation_service.py`
- [ ] T029 [US2] Integration test chunk matching with known test data in `backend/tests/integration/test_chunk_matching.py`
- [ ] T030 [US2] Contract test validation endpoint in `backend/tests/contract/test_validation_schema.py`

### Implementation for User Story 2

- [ ] T031 Create ValidationService in `backend/src/services/validation_service.py` with validate_chunks() method
- [ ] T032 [US2] Implement chunk text comparison logic in `backend/src/services/validation_service.py` (exact byte-for-byte match)
- [ ] T033 [P] [US2] Implement mismatch detection in `backend/src/services/validation_service.py` (length difference, truncation, corruption patterns)
- [ ] T034 [P] [US2] Implement ValidationResult model in `backend/src/models/validation_result.py` with match status and mismatch details
- [ ] T035 [US2] Add retrieval-time verification in RetrievalService (call ValidationService on results before returning)
- [ ] T036 [US2] Add logging for integrity issues in `backend/src/services/validation_service.py`

**Parallel Execution Suggestion** (T032-T034 can run in parallel after T031):
```
T031 (ValidationService creation)
  ├── T032 [P] (comparison logic)
  ├── T033 [P] (mismatch detection)
  └── T034 [P] (model)
  └── T035 (integration with retrieval - depends on above)
```

**Checkpoint**: User Stories 1-2 complete - retrieval with automatic data integrity verification

---

## Phase 5: User Story 3 - Retrieve Accurate Metadata for Retrieved Results (Priority: P1)

**Goal**: Return complete metadata (URL, chunk_id, position, timestamp) with every search result for traceability and attribution

**Independent Test**: Verify each search result includes complete metadata, URL and chunk_id are present and correct, metadata matches Qdrant payload

### Tests for User Story 3

- [ ] T037 [P] [US3] Unit test metadata extraction in `backend/tests/unit/test_metadata_extraction.py`
- [ ] T038 [US3] Integration test metadata accuracy in `backend/tests/integration/test_metadata_accuracy.py`
- [ ] T039 [P] [US3] Test metadata consistency across multiple results in `backend/tests/integration/test_metadata_accuracy.py`

### Implementation for User Story 3

- [ ] T040 [US3] Implement metadata extraction in RetrievalService.search() (extract from Qdrant payload)
- [ ] T041 [P] [US3] Implement metadata validation in `backend/src/utils/validators.py` (verify URL, chunk_id, timestamp format)
- [ ] T042 [P] [US3] Implement metadata deduplication/consistency check in `backend/src/services/retrieval_service.py`
- [ ] T043 [US3] Update RetrievalResponse to include metadata in each result
- [ ] T044 [US3] Add logging for metadata issues (missing fields, invalid URLs) in `backend/src/services/retrieval_service.py`
- [ ] T045 [US3] Add metadata to validation checks (ensure stored = returned)

**Parallel Execution Suggestion** (T041-T042 can run in parallel after T040):
```
T040 (metadata extraction)
  ├── T041 [P] (validation)
  ├── T042 [P] (consistency)
  └── T043 (response update - depends on above)
```

**Checkpoint**: User Stories 1-3 complete - full retrieval with integrity verification and metadata

---

## Phase 6: User Story 4 - Execute End-to-End Retrieval Pipeline with Clean JSON Output (Priority: P2)

**Goal**: Complete pipeline testing with structured JSON responses for all scenarios (success, empty results, errors)

**Independent Test**: Execute query → embedding → search → formatting end-to-end, validate JSON response structure, test error responses

### Tests for User Story 4

- [ ] T046 [P] [US4] Contract test complete response schema in `backend/tests/contract/test_response_schema.py` (success, error, empty results cases)
- [ ] T047 [US4] Integration test full pipeline with various query scenarios in `backend/tests/integration/test_end_to_end_retrieval.py`
- [ ] T048 [P] [US4] Test error responses (400 validation, 503 service unavailable) in `backend/tests/integration/test_error_handling.py`
- [ ] T049 [P] [US4] Test edge cases (empty Qdrant, no results, malformed input) in `backend/tests/integration/test_edge_cases.py`

### Implementation for User Story 4

- [ ] T050 [US4] Implement response formatting pipeline in `backend/src/utils/json_formatter.py` with ExecutionMetadata capture
- [ ] T051 [P] [US4] Implement query latency tracking in RetrievalService (capture timestamps, calculate total time)
- [ ] T052 [P] [US4] Implement error response formatting in `backend/src/utils/json_formatter.py` with HTTP status codes
- [ ] T053 [US4] Create API wrapper endpoints in `backend/src/api/retrieval.py`: POST /api/v1/retrieval/search
- [ ] T054 [US4] Create validation endpoint in `backend/src/api/retrieval.py`: POST /api/v1/retrieval/validate
- [ ] T055 [US4] Add input validation middleware in `backend/src/api/retrieval.py` (400 on invalid input)
- [ ] T056 [P] [US4] Implement graceful error handling for Qdrant/Cohere failures in `backend/src/api/retrieval.py` (503 responses)
- [ ] T057 [US4] Add comprehensive logging to API layer in `backend/src/api/retrieval.py`

**Parallel Execution Suggestion** (T051-T052 can run parallel with T050):
```
T050 (response formatting)
  ├── T051 [P] (latency tracking)
  ├── T052 [P] (error formatting)
  └── T053 (API search endpoint)
  └── T054 (API validate endpoint)
```

**Checkpoint**: All User Stories complete - full end-to-end pipeline with JSON responses

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, comprehensive testing, documentation, deployment readiness

### Performance & Scalability

- [ ] T058 [P] Performance test with 100+ concurrent queries in `backend/tests/performance/test_concurrent_queries.py` (target: < 2s latency)
- [ ] T059 [P] Test connection pooling and resource cleanup in `backend/tests/performance/test_connection_pooling.py`
- [ ] T060 Add query embedding caching in `backend/src/services/embedding_service.py` (optional: reduce Cohere API calls)

### Comprehensive Testing

- [ ] T061 Measure and report test coverage in `backend/` (target: > 80%)
- [ ] T062 Run full test suite and generate coverage report in `backend/tests/`

### Documentation

- [ ] T063 Update README.md with API usage examples and quickstart guide
- [ ] T064 Create developer guide for extending RetrievalService in `backend/docs/developer-guide.md`

### Configuration & Deployment

- [ ] T065 Create production configuration template in `backend/.env.production.example`
- [ ] T066 Create Docker setup files (Dockerfile, docker-compose.yml) in `backend/`
- [ ] T067 Document deployment instructions in `backend/docs/deployment.md`

---

## Task Dependencies & Completion Order

### Critical Path (Minimum for MVP):
```
Phase 1 (Setup)
  → Phase 2 (Foundation: T006-T016)
    → Phase 3 (US1: T017-T027)
      → Phase 4 (US2: T028-T036)
        → Phase 5 (US3: T037-T045)
          → Phase 6 (US4: T046-T057)
```

### Parallelization Opportunities:
- **Phase 2**: All T006-T015 can run in parallel (except T013-T014 depend on T006-T009)
- **Phase 3**: T023-T025 can run in parallel after T022
- **Phase 4**: T032-T034 can run in parallel after T031
- **Phase 5**: T041-T042 can run in parallel after T040
- **Phase 6**: T051-T052 can run in parallel with T050; T048-T049 can run with T046-T047
- **Phase 7**: All tasks can run in parallel (independent of functionality)

### User Story Dependency Graph:
```
Foundation (Phase 2)
  ├── US1 (Phase 3) - Independent MVP
  ├── US2 (Phase 4) - Depends on: US1 working (retrieval results to validate)
  ├── US3 (Phase 5) - Depends on: US1 (metadata in results)
  └── US4 (Phase 6) - Depends on: US1, US2, US3 (orchestrate all into JSON)
```

All user stories can be independently tested once foundation is complete.

---

## Independent Test Criteria per User Story

### User Story 1 Complete When:
✅ RetrievalService.search() returns results ranked by similarity score
✅ Results limited to top_k parameter
✅ Threshold filtering works
✅ Integration test passes with known test data

### User Story 2 Complete When:
✅ ValidationService detects exact text matches
✅ Validation detects truncation and corruption
✅ All retrieved chunks verified before return
✅ Integration test passes comparing original vs retrieved

### User Story 3 Complete When:
✅ Each search result includes URL and chunk_id metadata
✅ Metadata matches Qdrant payload exactly
✅ Metadata validation catches missing/invalid fields
✅ Integration test passes metadata accuracy checks

### User Story 4 Complete When:
✅ JSON response structure matches OpenAPI schema
✅ All required fields present (query, status, results, execution, errors)
✅ Error responses formatted correctly with status codes
✅ End-to-end pipeline latency < 2 seconds

---

## Success Metrics (from spec.md)

- **SC-001**: Retrieved chunks exactly match original extracted content with 100% accuracy → Verified by US2 tests
- **SC-002**: Metadata (url, chunk_id) is returned correctly for 100% of search results → Verified by US3 tests
- **SC-003**: Search results ranked by relevance with top result having highest similarity score for 95%+ of queries → Verified by US1 tests
- **SC-004**: End-to-end retrieval pipeline completes within 2 seconds for typical queries → Verified by US4 tests + performance tests
- **SC-005**: JSON response payload is valid and parseable for 100% of successful queries → Verified by US4 contract tests
- **SC-006**: System handles 100+ concurrent queries without performance degradation → Verified by T058
- **SC-007**: Queries return semantically relevant results for 90%+ of real-world test cases → Verified by T047

---

## Total Task Count: 67 Tasks

- **Phase 1** (Setup): 5 tasks
- **Phase 2** (Foundation): 11 tasks
- **Phase 3** (US1): 11 tasks
- **Phase 4** (US2): 9 tasks
- **Phase 5** (US3): 9 tasks
- **Phase 6** (US4): 8 tasks
- **Phase 7** (Polish): 9 tasks

**Estimated Execution Order**: Foundation (Phase 1-2) must complete first. User stories (Phase 3-6) can then proceed with internal parallelization. Polish phase runs last.
