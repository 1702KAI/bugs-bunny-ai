# 🐰 Bugs Bunny AI Hackathon - Technical Assessment Grading

**Candidate:** Thinal  
**Date:** February 6, 2026  
**Assessor:** Senior Technical Assessor

---

## 📊 Grading Breakdown

### 1. Git Usage (20 Points)

| Criteria | Status | Score |
|----------|--------|-------|
| Repository forked/cloned | ✅ Yes | 5/5 |
| Correct branch (`feature/add-tasks-api`) | ✅ Yes | 5/5 |
| Clear commit messages | ⚠️ Partial | 3/5 |
| Merge conflicts resolved | ✅ N/A (no conflicts) | 5/5 |

**Score: 18/20**

**Feedback:** The candidate correctly worked on the `feature/add-tasks-api` branch. However, with only 2 commits (`boilerplate code` → `feat: implement tasks API and fix utility bugs`), the commit history is minimal. Best practice would be to have more granular commits (e.g., separate commits for bug fixes vs. feature implementation).

---

### 2. Feature Implementation (25 Points)

| Criteria | Status | Score |
|----------|--------|-------|
| **POST /tasks** | | |
| - Priority validation (low/medium/high/critical) | ✅ Implemented with case-insensitive handling | 5/5 |
| - User existence verification | ✅ Returns 404 if user not found | 5/5 |
| - Auto-generate IDs | ✅ Uses incrementing counter | 3/3 |
| **GET /tasks** | | |
| - Filter by email, status, priority | ✅ All filters implemented | 4/4 |
| - Sort by priority_score, due_date, created_at | ✅ All sort options work | 4/4 |
| **Response codes (201, 400, 404)** | ✅ Correct codes used | 4/4 |

**Score: 25/25**

**Feedback:** Excellent implementation! The POST endpoint properly validates all fields, sanitizes title input, normalizes priority to lowercase, and auto-generates sequential IDs. The GET endpoint supports comprehensive filtering and sorting with proper edge case handling (e.g., tasks without due dates).

---

### 3. Code Quality (15 Points)

| Criteria | Status | Score |
|----------|--------|-------|
| Clean, modular code | ✅ Well-structured | 5/5 |
| Python best practices | ✅ Dataclasses, type hints, docstrings | 4/5 |
| Input sanitization | ✅ XSS protection via `sanitize_input()` | 5/5 |
| Code organization | ✅ Proper separation (models, utils, main) | — |

**Score: 14/15**

**Feedback:** The code is clean and follows Python conventions with:
- Proper use of dataclasses in `app/models.py`
- Comprehensive docstrings
- Good separation of concerns
- Effective use of regex for sanitization

Minor deduction: Could benefit from type hints on the Flask route functions.

---

### 4. Bug Fixes (25 Points)

| Function | Bug Fixed | Tests Pass | Score |
|----------|-----------|------------|-------|
| `validate_email()` | ✅ Replaced permissive `.+@.+` with RFC 5322 pattern | ✅ 6/6 | 6/6 |
| `calculate_priority_score()` | ✅ Fixed off-by-one (`<` → `<=`) + added error handling | ✅ 6/6 | 7/7 |
| `sanitize_input()` | ✅ Added case-insensitive regex, event handlers, JS URLs | ✅ 6/6 | 6/6 |
| `parse_date()` | ✅ Added proper error handling with descriptive messages | ✅ 4/4 | 6/6 |

**All 22 tests pass:** ✅

**Score: 25/25**

**Feedback:** Outstanding bug fix work! The candidate identified and fixed all 7+ bugs across the 4 core functions:
1. Email regex was overly permissive
2. Off-by-one errors in priority score boundaries
3. Missing `ValueError` handling for invalid priorities
4. Case-sensitive script tag removal
5. Missing event handler sanitization
6. Missing JavaScript URL removal
7. Improved `parse_date()` error messages

---

### 5. Documentation (10 Points)

| Document | Criteria | Status | Score |
|----------|----------|--------|-------|
| **REVIEW_NOTES.md** | | | |
| - Input length question (10,000 chars) | ✅ Thoroughly analyzed with recommendations | 3/3 |
| - Case sensitivity question | ✅ Explained with code examples | 3/3 |
| **BUG_REPORT.md** | | | |
| - Root cause analysis | ✅ Detailed for all 7 bugs | 2/2 |
| - Fix descriptions | ✅ Before/after code with explanations | 2/2 |

**Score: 10/10**

**Feedback:** Exceptional documentation! Both files are professional, well-structured, and demonstrate deep understanding:
- `REVIEW_NOTES.md` provides security analysis with tables, code examples, and prioritized recommendations
- `BUG_REPORT.md` includes expected vs. actual behavior tables, root cause analysis, and test results

---

### 6. Reflection (5 Points)

| Criteria | Status | Score |
|----------|--------|-------|
| Implementation summary | ⚠️ Partial (in BUG_REPORT.md summary section) | 2/3 |
| AI tool usage reflection | ❌ Not found | 0/2 |

**Score: 2/5**

**Feedback:** The candidate provided a good summary of bugs found and security implications in the BUG_REPORT.md, but there is **no explicit reflection on AI tool usage** as required by the rubric. The README.md is empty, which would have been an ideal place for this reflection.

---

## 📈 Final Score

| Category | Points Earned | Max Points |
|----------|---------------|------------|
| Git Usage | 18 | 20 |
| Feature Implementation | 25 | 25 |
| Code Quality | 14 | 15 |
| Bug Fixes | 25 | 25 |
| Documentation | 10 | 10 |
| Reflection | 2 | 5 |
| **TOTAL** | **94** | **100** |

---

## 🏆 Result: **PASS** ✅

**Score: 94/100** (Passing threshold: 70)

---

## 📝 Summary Feedback

### Strengths
1. **Excellent bug fixing skills** - All 22 tests pass with comprehensive fixes
2. **Complete feature implementation** - Both POST and GET endpoints fully functional
3. **Outstanding documentation** - Professional, detailed security analysis
4. **Strong security awareness** - XSS protection, input validation, proper error handling
5. **Clean code architecture** - Well-organized, modular design

### Areas for Improvement
1. **Git hygiene** - Use more granular commits (separate bug fixes from features)
2. **Missing reflection** - Add an AI tool usage reflection section
3. **Empty README** - Should contain project overview and setup instructions
4. **Length validation** - As noted in REVIEW_NOTES.md, title length limits are recommended but not implemented

### Recommendation
**Strong candidate.** Demonstrates solid Python skills, security awareness, and excellent documentation practices. The minor deductions are primarily procedural (git commits, reflection) rather than technical.
