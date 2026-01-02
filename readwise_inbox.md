---
created: 2025-12-28
changelog:
  - 2025-12-28: Initial creation
  - 2025-12-28: Refactored to "co-founder" workflow - Readwise as inbox, markdown as archive
  - 2026-01-01: Added numbered format for easier item selection during review
  - 2026-01-01: Added parallel WebFetch for faster deep dives on multiple items
  - 2026-01-01: Made archiving mandatory at end of every review session
---

# Directive: Readwise Captures

> **Orchestration:** User shares links (tweets, YouTube, articles) to Readwise Reader like texting a co-founder. When they ask, you pull from Readwise, review together, and archive to weekly markdown files.

## Purpose
Give the user a "co-founder" experience for capturing and reviewing content they find online. They share things throughout their day, then we review together and determine what's useful for current projects.

## Mental Model

| Component | Role |
|-----------|------|
| **Readwise** | Inbox — where new stuff lands |
| **Weekly markdown files** | Archive — reviewed items with relevance notes |
| **You (Claude)** | The co-founder who checks the inbox and helps assess |

## Workflow

### 1. User Shares Content
User saves links to Readwise Reader via share sheet (iPhone/Mac). No action needed from you.

### 2. User Asks to Review
When user says things like:
- "Check what I sent you"
- "What's new?"
- "Look at my captures"
- "Review my Readwise"

**Do this:**

1. **Pull new items from Readwise**
   ```bash
   python execution/fetch_readwise.py --days 7
   ```
   Or use the Python directly to fetch and display.

2. **Show what's new** — Present items in numbered format for easy selection:
   ```
   **1. Author/Source — Title**
   - Key point 1
   - Key point 2
   - Application: How it's relevant

   **2. Author/Source — Title**
   ...
   ```
   Group by theme (e.g., "Sales & GTM", "Workflow", etc.) when helpful.
   User can then say "keep 1, 3, 5" or "dig into 4" for quick communication.

3. **For each item, assess relevance:**
   - Check `CLAUDE.md` for project context
   - Check `directives/` for active workflows
   - Note: What could this help with? Any actionable insights?

4. **Discuss with user** — Call out anything especially useful, ask if they want to dig deeper on anything

### 3. Deep Dive (On Request)
When user wants full content from specific items:

1. **Fetch full content in parallel**
   - For Readwise content (tweets, videos with transcripts):
     ```bash
     python execution/fetch_readwise.py --with-content --days 7
     ```
   - For articles/external URLs: Use WebFetch tool
   - **Run all WebFetch calls in parallel** (single message, multiple tool calls) for speed

2. **Read the full transcript/thread/article**

3. **Synthesize learnings** — numbered format (see Self-Annealing Notes)

4. **Note what's actionable** for their projects

### 4. Archive to Weekly File (ALWAYS DO THIS)
**Before ending any review session**, archive reviewed items:

1. **Run the archive script** to save reviewed items:
   ```bash
   python execution/archive_readwise.py
   ```

2. **Update relevance notes** in the weekly file based on our discussion

3. **Confirm** — "Archived X items to captures/MM.DD.YY.md"

## Tools

| Tool | Purpose |
|------|---------|
| `execution/fetch_readwise.py` | Pull items from Readwise API (for live review) |
| `execution/archive_readwise.py` | Archive items to weekly markdown files |

### Fetch Options
```bash
# Recent items (last 7 days)
python execution/fetch_readwise.py --days 7

# Just tweets
python execution/fetch_readwise.py --category tweet

# Just videos
python execution/fetch_readwise.py --category video

# With full content (transcripts, threads)
python execution/fetch_readwise.py --with-content --limit 5
```

### Archive Options
```bash
# Archive new items to weekly files
python execution/archive_readwise.py

# Only specific category
python execution/archive_readwise.py --category tweet

# Reprocess all (ignore tracking)
python execution/archive_readwise.py --reprocess
```

## Output

**Weekly archive files:** `captures/MM.DD.YY.md`
- Named by the Sunday that starts the week
- Example: `12.28.25.md` for week of Dec 28 - Jan 3

**File format:**
```markdown
# Captures: Dec 28 - Jan 03, 2026

## Tweet: Title here
**Author**: @handle
**Saved**: 2025-12-28
**Link**: https://x.com/...

Summary of the content.

**Relevance**: Useful for X project because Y. Key insight: Z.

---
```

## Edge Cases

### RSS Feed Noise
Readwise may include RSS items from subscriptions. Skip these during review unless relevant, or user can unsubscribe in Readwise.

### Full Transcript Access
Summaries are quick to scan, but full content (YouTube transcripts, full Twitter threads) is always available via `--with-content` flag when deeper analysis is needed.

### API Rate Limits
Readwise has a 20 requests/minute limit. Shouldn't be an issue under normal use.

## Self-Annealing Notes
_This section gets updated as we learn more about the workflow_

### Co-founder feel (2025-12-28)
The user wants this to feel like texting a co-founder: "Hey, found this — take a look." The key is responsiveness and relevance assessment, not just processing. Always tie back to current projects when reviewing.

### Numbered format (2026-01-01)
Two stages of numbering for easy selection:

**Stage 1 — Initial review:** Number raw Readwise items (1-8) so user can say "dig into 3" or "skip 7"

**Stage 2 — After synthesis:** Number the summarized learnings/insights too, so user can say "save insight 2 to future_ideas" or "act on 1 and 5"

Example synthesis format:
```
## Synthesized Learnings

**1. Pain > Upside (Jeanne DeWitt)**
- "Customers buy to avoid pain rather than gain upside"
- Application: Reframe email copy around avoiding pain

**2. Voice of Customer Mining (Mario Nawfal)**
- Framework: Audience replies → AI analysis → data-backed messaging
- Application: Add to research directive
```

Group by theme when there are multiple categories (Sales, Workflow, etc.).

### Parallel fetching (2026-01-01)
When doing deep dives on multiple items, run all WebFetch calls in parallel (single message with multiple tool calls). This is much faster than sequential fetching. Future upgrade: Perplexity API for richer synthesis.

### Always archive (2026-01-01)
Never end a review session without running `archive_readwise.py`. This ensures nothing gets lost between sessions. Make it the last step before wrapping up.
