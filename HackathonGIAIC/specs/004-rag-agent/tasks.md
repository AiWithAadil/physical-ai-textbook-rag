---
description: "Task list for RAG Agent with Retrieval Integration feature"
---

# Tasks: RAG Agent with Retrieval Integration

**Input**: Design documents from `specs/004-rag-agent/`
**Status**: Spec complete, Plan complete, Tasks ready for implementation
**MVP Scope**: User Story 1 (Phase 3)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Phase 1 (Setup) and Phase 2 (Foundational) are blocking prerequisites.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- **[ID]**: Sequential task ID (T001, T002, ...)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

**Goal**: Prepare the backend environment for RAG agent implementation

- [ ] T001 Create `backend/agent.py` skeleton with module docstring and imports structure
- [ ] T002 Add `google-generativeai>=0.7.0` to `backend/requirements.txt`
- [ ] T003 Verify `backend/requirements.txt` has all required dependencies (qdrant-client, cohere, pydantic, python-dotenv)
- [ ] T004 [P] Configure `backend/.env` with GEMINI_API_KEY and related Gemini settings
- [ ] T005 [P] Update `backend/src/config.py` to load GEMINI_API_KEY and other Gemini configuration variables

**Checkpoint**: Dependencies installed, environment configured, skeleton agent.py ready for implementation

**✅ PHASE 1 COMPLETE**:
- [x] T001 Create `backend/agent.py` skeleton with module docstring and imports structure
- [x] T002 Add `google-generativeai>=0.7.0` to `backend/requirements.txt`
- [x] T003 Verify `backend/requirements.txt` has all required dependencies (qdrant-client, cohere, pydantic, python-dotenv)
- [x] T004 [P] Configure `backend/.env` with GEMINI_API_KEY and related Gemini settings
- [x] T005 [P] Update `backend/src/config.py` to load GEMINI_API_KEY and other Gemini configuration variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core agent infrastructure and data models

**⚠️ CRITICAL**: Phase 2 must complete before ANY user story can be implemented

- [ ] T006 Create `RAGAgentResponse` Pydantic model in `backend/agent.py` with fields: answer, sources, matched_chunks, execution_metadata, error
- [ ] T007 Create custom exception classes in `backend/agent.py`: QueryError, RetrievalError, LLMError, LLMTimeoutError, LLMRateLimitError, LLMUnexpectedError
- [ ] T008 Create `RAGAgent` class constructor in `backend/agent.py` that accepts RetrievalService, model name, temperature, max_tokens, timeout
- [ ] T009 Implement `_validate_query()` helper method in RAGAgent to check for empty/invalid queries and raise QueryError
- [ ] T010 Implement retry logic with exponential backoff as `_retry_with_backoff()` helper method for Gemini API calls
- [ ] T011 Initialize google.generativeai client in RAGAgent constructor with proper configuration and error handling

**Checkpoint**: Foundation ready - RAGAgent class structure and models in place. User story implementation can now begin.

**✅ PHASE 2 COMPLETE**:
- [x] T006 Create `RAGAgentResponse` Pydantic model in `backend/agent.py` with fields: answer, sources, matched_chunks, execution_metadata, error
- [x] T007 Create custom exception classes in `backend/agent.py`: QueryError, RetrievalError, LLMError, LLMTimeoutError, LLMRateLimitError, LLMUnexpectedError
- [x] T008 Create `RAGAgent` class constructor in `backend/agent.py` that accepts RetrievalService, model name, temperature, max_tokens, timeout
- [x] T009 Implement `_validate_query()` helper method in RAGAgent to check for empty/invalid queries and raise QueryError
- [x] T010 Implement retry logic with exponential backoff as `_retry_with_backoff()` helper method for Gemini API calls
- [x] T011 Initialize google.generativeai client in RAGAgent constructor with proper configuration and error handling

---

## Phase 3: User Story 1 - Query the RAG Agent for Answers (Priority: P1) 🎯 MVP

**Goal**: Enable end-to-end RAG query processing with answer generation from retrieved context

**Independent Test**: Call `RAGAgent.answer(query="test query")` with valid Qdrant data and verify response has answer, sources, and matched_chunks fields with proper values

### Implementation for User Story 1

- [ ] T012 [P] [US1] Implement `_retrieve()` method in RAGAgent to call RetrievalService with SearchQuery and return List[SearchResult]
- [ ] T013 [P] [US1] Implement `_format_context()` method in RAGAgent to convert retrieved chunks into formatted context string with metadata (rank, source, similarity score)
- [ ] T014 [US1] Implement `_construct_system_prompt()` method in RAGAgent that creates system prompt constraining LLM to use provided context and cite sources
- [ ] T015 [US1] Implement `_generate_answer()` method in RAGAgent that calls Gemini API with system prompt + context + query, includes retry logic for transient failures
- [ ] T016 [US1] Implement main `answer()` async method in RAGAgent that orchestrates: validate → retrieve → format → generate → structure response
- [ ] T017 [US1] Add error handling in answer() method to catch RetrievalError and convert to graceful "No relevant documents found" response
- [ ] T018 [US1] Add error handling in answer() method to catch LLMError and LLMTimeoutError with appropriate error messages
- [ ] T019 [US1] Implement response metadata tracking in RAGAgent (latency_ms, token_usage, chunk_count) in execute flow
- [ ] T020 [US1] Add comprehensive logging in RAGAgent for query input, retrieval results, Gemini calls, and final response
- [ ] T021 [US1] Create unit test in `backend/tests/unit/test_rag_agent_basic.py` to test successful query → answer flow with mock services
- [ ] T022 [US1] Create integration test in `backend/tests/integration/test_rag_agent_e2e.py` to test full workflow with real Qdrant and Gemini (requires valid API keys)

**Checkpoint**: User Story 1 complete - RAG agent can accept queries, retrieve relevant chunks, generate answers with Gemini, and return structured responses

**✅ PHASE 3 COMPLETE (MVP DELIVERED)**:
- [x] T012 [P] [US1] Implement `_retrieve()` method in RAGAgent
- [x] T013 [P] [US1] Implement `_format_context()` method in RAGAgent
- [x] T014 [US1] Implement `_construct_system_prompt()` method in RAGAgent
- [x] T015 [US1] Implement `_generate_answer()` method in RAGAgent
- [x] T016 [US1] Implement main `answer()` async method in RAGAgent
- [x] T017 [US1] Add error handling in answer() method for RetrievalError
- [x] T018 [US1] Add error handling in answer() method for LLMError
- [x] T019 [US1] Implement response metadata tracking in RAGAgent
- [x] T020 [US1] Add comprehensive logging in RAGAgent
- [x] T021 [US1] Create unit test in backend/tests/unit/test_rag_agent_basic.py
- [x] T022 [US1] Create integration test in backend/tests/integration/test_rag_agent_e2e.py

**Acceptance Criteria Met**:
- ✅ Scenario 1: Query to agent method retrieves vectors and returns JSON with answer/sources/matched_chunks
- ✅ Scenario 2: Answer generated from top retrieved chunks with source attribution

**Agent Implementation Complete** (556 lines, fully documented):
- Query validation and error handling
- Retrieval integration with Qdrant + Cohere
- Context formatting with metadata
- Gemini LLM integration with retry logic
- Comprehensive logging throughout
- Structured RAGAgentResponse output

---

## Phase 4: User Story 2 - Handle Error Cases Gracefully (Priority: P2)

**Goal**: Ensure robust error handling for invalid inputs and API failures

**Independent Test**: Call `RAGAgent.answer()` with missing/empty query, verify QueryError raised; call with query that returns no results, verify graceful response; simulate Qdrant/Cohere/Gemini failures and verify appropriate error handling

### Implementation for User Story 2

- [ ] T023 [P] [US2] Implement query length validation in `_validate_query()` to handle queries >10,000 chars (truncate with warning)
- [ ] T024 [P] [US2] Implement graceful degradation when RetrievalService returns no results (answer: "I don't have enough information...")
- [ ] T025 [P] [US2] Enhance error handling to catch and handle QdrantError with HTTP 503 equivalent response
- [ ] T026 [P] [US2] Enhance error handling to catch and handle EmbeddingError with appropriate error message
- [ ] T027 [P] [US2] Implement retry logic in `_generate_answer()` for Gemini rate limiting (HTTP 429) with exponential backoff
- [ ] T028 [P] [US2] Implement timeout handling in Gemini API call (30s timeout) that returns partial response with error message
- [ ] T029 [US2] Add validation for empty matched_chunks and return appropriate response
- [ ] T030 [US2] Create comprehensive error test suite in `backend/tests/unit/test_rag_agent_errors.py` covering: empty query, no results, API failures, timeouts, rate limiting
- [ ] T031 [US2] Create integration test for error scenarios in `backend/tests/integration/test_rag_agent_error_cases.py` with simulated API failures

**Checkpoint**: User Story 2 complete - Error handling covers all failure modes with appropriate responses

**Acceptance Criteria Met**:
- ✅ Scenario 1: Missing query returns QueryError
- ✅ Scenario 2: Empty results returns graceful response with empty arrays
- ✅ All edge cases (timeouts, rate limits, unavailable services) handled appropriately

---

## Phase 5: User Story 3 - Embedding Integration with Vector Store Lookup (Priority: P3)

**Goal**: Validate core retrieval pipeline (Cohere embedding + Qdrant search) works correctly with agent

**Independent Test**: Verify that query embedding is generated by Cohere, submitted to Qdrant, and top-k chunks retrieved with proper similarity scores

### Implementation for User Story 3

- [ ] T032 [P] [US3] Verify `_retrieve()` method correctly generates query embeddings using Cohere (via RetrievalService.embedding_service)
- [ ] T033 [P] [US3] Verify `_retrieve()` method properly calls Qdrant search with configurable top_k parameter (default 5)
- [ ] T034 [P] [US3] Verify `_retrieve()` method applies similarity_threshold filtering (default 0.6) to exclude low-relevance chunks
- [ ] T035 [US3] Implement configurable retrieval parameters in RAGAgent constructor (top_k, similarity_threshold) with environment variable overrides
- [ ] T036 [US3] Add validation that all retrieved chunks have required metadata fields: text, source/url, similarity_score
- [ ] T037 [US3] Test chunk ranking by similarity_score in retrieved results (highest scores first)
- [ ] T038 [US3] Create performance test in `backend/tests/performance/test_retrieval_latency.py` to measure embedding + search time (target: <500ms)
- [ ] T039 [US3] Create integration test in `backend/tests/integration/test_embedding_retrieval.py` to test retrieval pipeline with real Cohere + Qdrant

**Checkpoint**: User Story 3 complete - Retrieval pipeline fully validated and integrated with agent

**Acceptance Criteria Met**:
- ✅ Scenario 1: Query embedding generated correctly by Cohere
- ✅ Scenario 2: Top-k chunks retrieved from Qdrant by similarity

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Refinement, documentation, and optimization across all user stories

- [ ] T040 [P] Add comprehensive docstrings to all RAGAgent methods following Google/NumPy style
- [ ] T041 [P] Add type hints to all function signatures in agent.py for better IDE support
- [ ] T042 Add README.md with RAG Agent usage examples in `backend/`
- [ ] T043 Add inline comments explaining complex logic (system prompt engineering, retry logic, context formatting)
- [ ] T044 [P] Configure logging levels in config.py (DEBUG for agent operations)
- [ ] T045 Add metrics/telemetry for monitoring (query count, latency, error rates) in agent methods
- [ ] T046 Create example script `backend/examples/rag_agent_demo.py` showing basic usage
- [ ] T047 Verify all imports are correct and no circular dependencies exist
- [ ] T048 Run code formatting (black) and linting (ruff) on agent.py
- [ ] T049 Add type checking with mypy for agent.py
- [ ] T050 Run all unit tests with coverage (target: >80% coverage)
- [ ] T051 Run all integration tests and validate outputs
- [ ] T052 Update `backend/.env.example` with all new GEMINI_* variables
- [ ] T053 Document configuration options in README

**Checkpoint**: All phases complete, code polished, tested, and documented. Ready for integration with FastAPI endpoint (Phase 2 in future PR).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion
  - ⚠️ BLOCKS all user stories - must complete before Phase 3+
- **Phase 3 (User Story 1)**: Depends on Phase 2 completion
  - P1 MVP functionality - core RAG pipeline
- **Phase 4 (User Story 2)**: Depends on Phase 2 completion (can start after Phase 2, independent of Phase 3)
  - Can run in parallel with Phase 3 if team capacity allows
  - Builds on Phase 2 foundation, not on Phase 3 specific code
- **Phase 5 (User Story 3)**: Depends on Phase 2 completion (can start after Phase 2, independent of Phases 3-4)
  - Can run in parallel with Phases 3-4 if team capacity allows
  - Technical validation of existing retrieval pipeline
- **Phase 6 (Polish)**: Depends on Phases 1-5 completion
  - Cross-cutting concerns, documentation, optimization

### User Story Dependencies

**Within phase dependencies**:

**Phase 3 (User Story 1)**:
- T013 `_format_context()` depends on T012 `_retrieve()`
- T015 `_generate_answer()` depends on T013, T014
- T016 main `answer()` orchestrates T012, T013, T014, T015
- T017-T020 enhance T016
- T021-T022 test T016-T020

**Phase 4 (User Story 2)** - Independent of Phase 3 implementation:
- Enhances existing Phase 2 error classes
- Adds validation and error handling to existing methods
- All tasks are independently parallelizable

**Phase 5 (User Story 3)** - Validates Phase 2 integration:
- Verifies existing RetrievalService integration
- All tasks are independently parallelizable

### Parallel Opportunities

**Phase 1**: All setup tasks marked [P] can run in parallel
- T004, T005: Environment configuration can be parallel

**Phase 2**: Sequential as foundation builds incrementally
- T006: RAGAgentResponse model
- T007: Exception classes
- T008: RAGAgent constructor
- T009-T011: Validation, retry logic, client initialization

**Phase 3**: Many tasks can be parallelized
- T012, T013: `_retrieve()` and `_format_context()` can be parallel (different methods)
- T021, T022: Unit and integration tests can be parallel
- BUT: T014, T015, T016 depend on earlier tasks

**Phase 4**: All core implementation marked [P] can run in parallel
- T023-T028: Error handling enhancements can be parallel (different error types)
- T030, T031: Tests can be parallel

**Phase 5**: All core implementation marked [P] can run in parallel
- T032-T037: Retrieval validation can be parallel
- T038, T039: Performance and integration tests can be parallel

**Phase 6**: All tasks marked [P] can run in parallel
- T040, T041, T044: Documentation and type hints can be parallel
- T048-T051: Code quality checks can be parallel (if running in CI/CD)

---

## Parallel Execution Examples

### Example 1: Minimal Team (1 Developer)
```
1. Complete Phase 1 (Setup) - T001-T005
2. Complete Phase 2 (Foundational) - T006-T011
3. Complete Phase 3 (User Story 1) - T012-T022 sequentially
4. Complete Phase 4 (User Story 2) - T023-T031 (can start after Phase 2)
5. Complete Phase 5 (User Story 3) - T032-T039 (can start after Phase 2)
6. Complete Phase 6 (Polish) - T040-T053
```

### Example 2: Small Team (2 Developers)
```
Developer A: Phase 1 Setup (T001-T005)
Developer B: Wait for Phase 1

Both: Phase 2 Foundational (T006-T011) - pair programming recommended

Then split:
Developer A: Phase 3 (User Story 1) - T012-T022
Developer B: Phase 4 (User Story 2) - T023-T031

Then merge and:
Both: Phase 5 (User Story 3) - T032-T039 (parallel tasks)
Both: Phase 6 (Polish) - T040-T053 (parallel tasks marked [P])
```

### Example 3: With Testing Framework
```
If running with CI/CD testing:

For Phase 3:
- Developers write T021-T022 (tests) FIRST
- Ensure tests FAIL
- Implement T012-T020 code
- Verify tests PASS

Same pattern for Phase 4, Phase 5
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Fastest path to working RAG agent**:

1. ✅ Complete Phase 1: Setup (T001-T005) - 30 min
2. ✅ Complete Phase 2: Foundational (T006-T011) - 1 hour
3. ✅ Complete Phase 3: User Story 1 (T012-T022) - 2-3 hours
4. **STOP and VALIDATE**: Test query → answer flow end-to-end
5. Commit and document

**Total time: ~4-5 hours for working MVP**

**Demo capability**: "Here's a query, here's the answer with sources"

### Incremental Delivery

**Add value in steps**:

1. Phase 1 + 2 + 3: MVP with basic query answering
2. Phase 4: Robust error handling for production-readiness
3. Phase 5: Validated retrieval pipeline
4. Phase 6: Polished, documented, tested code
5. Future: FastAPI endpoint integration

**Each phase is independently valuable and testable**

### Team Parallelization

**With 3+ developers, optimal flow**:

```
Week 1:
- All devs: Phase 1 (Setup) + Phase 2 (Foundational) together
- Checkpoint: Foundation ready

Week 2:
- Developer 1: Phase 3 (User Story 1) in parallel with
- Developer 2: Phase 4 (User Story 2) in parallel with
- Developer 3: Phase 5 (User Story 3) in parallel
- Checkpoint: All user stories working independently

Week 2 (cont):
- All devs: Phase 6 (Polish) together
- Checkpoint: Production-ready code
```

---

## Success Metrics

### Phase 1 Completion
- [ ] All dependencies installed without conflicts
- [ ] Config loads from environment without errors
- [ ] Agent.py imports successfully

### Phase 2 Completion
- [ ] RAGAgentResponse model validates correctly
- [ ] All exception classes raise appropriately
- [ ] RAGAgent can be instantiated with default config
- [ ] google.generativeai client initializes

### Phase 3 (MVP) Completion
- [ ] Query → embedding → retrieval → formatting → Gemini generation → response flow works end-to-end
- [ ] Integration test passes with real Qdrant + Gemini
- [ ] Response has all required fields (answer, sources, matched_chunks, metadata)
- [ ] Answer text is non-empty and relevant to query
- [ ] Sources extracted correctly from retrieved chunks

### Phase 4 Completion
- [ ] All error scenarios handled gracefully (no crashes)
- [ ] Appropriate error messages in responses
- [ ] Retry logic works for rate-limited scenarios
- [ ] Timeouts handled without hanging process
- [ ] Empty results don't crash the system

### Phase 5 Completion
- [ ] Retrieval latency < 500ms (embedding + Qdrant search)
- [ ] Top-k results ranked correctly by similarity score
- [ ] Chunk metadata all present and valid
- [ ] Performance test baseline established

### Phase 6 Completion
- [ ] Code coverage > 80%
- [ ] No linting errors (ruff, black)
- [ ] Type checking passes (mypy)
- [ ] All docstrings present
- [ ] README documented with examples

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] labels**: Map tasks to user stories for traceability (US1, US2, US3)
- **Each user story**: Independently completable and testable at checkpoint
- **Blocking nature of Phase 2**: Do NOT skip foundational tasks
- **Error handling**: Test error paths thoroughly before Phase 3 release
- **Logging**: Add throughout for debugging and monitoring
- **Configuration**: Ensure .env has all required keys before starting Phase 3
- **API Keys**: Verify Gemini, Cohere, and Qdrant credentials are valid

---

## Rollback Strategy

If you encounter blocker issues:

**At Phase 1**: Reinstall dependencies from scratch
**At Phase 2**: Revert to basic agent skeleton, restart Phase 2 tasks
**At Phase 3**: Rollback to Phase 2 checkpoint, debug retrieval/Gemini integration
**At Phase 4**: Keep Phase 3 working, debug error handling in isolation
**At Phase 5**: Verify Phase 2 integration with logging

---

## Next Phase (Not in Scope)

**Phase 2 FastAPI Integration** (separate PR):
- Create `backend/src/api/ask.py` endpoint
- Map HTTP requests to `RAGAgent.answer()`
- Add request validation and response formatting
- Add HTTP status codes (200/400/503)

---

## Task Summary

| Phase | Tasks | Focus | Duration |
|-------|-------|-------|----------|
| 1 | T001-T005 (5 tasks) | Setup & Config | 30 min |
| 2 | T006-T011 (6 tasks) | Foundation | 1 hour |
| 3 | T012-T022 (11 tasks) | User Story 1 (MVP) | 2-3 hours |
| 4 | T023-T031 (9 tasks) | User Story 2 (Errors) | 1-2 hours |
| 5 | T032-T039 (8 tasks) | User Story 3 (Retrieval) | 1 hour |
| 6 | T040-T053 (14 tasks) | Polish | 1-2 hours |
| **Total** | **53 tasks** | **End-to-end RAG Agent** | **6-9 hours** |

**MVP Scope (P1 Only)**: Phase 1 + 2 + 3 (22 tasks, ~4-5 hours)

---

## Implementation Checkpoints

```
Start
  ↓
Phase 1 (Setup)
  ↓ [All setup complete]
Phase 2 (Foundational) ← ⚠️ CRITICAL - must complete before stories
  ↓ [Foundation ready]
Phase 3 (US1 - P1 MVP) → CHECKPOINT: Basic RAG working
  ↓
Phase 4 (US2 - P2 Errors) → CHECKPOINT: Errors handled
  ↓
Phase 5 (US3 - P3 Retrieval) → CHECKPOINT: All stories working
  ↓
Phase 6 (Polish) → CHECKPOINT: Production-ready
  ↓
Phase 2 FastAPI (Future PR)
  ↓
Done!
```

