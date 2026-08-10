# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Pre-implementation. The repository is empty; this file is the design contract agreed before the first commit, not a description of existing code. Update it as code lands — especially the Commands section, which is currently empty because there is nothing to run.

## What this is

A daily pipeline that harvests agentic-AI news from many sources, clusters it across sources, scores it, and surfaces 5–10 ranked seeds per week for a 3-post-per-week LinkedIn cadence. Most seeds get rejected downstream; that rejection rate is the system working, not a bug to tune away.

Deliberately excluded: anything drawn from the author's client work. The system has no personal-experience input and must not acquire one.

## The core idea, and why the architecture looks like this

"Reads AI newsletters, posts summaries" is a crowded lane. The differentiation is the **corpus**: every fetched item is stored forever, so after a few weeks the system can make claims no single source supports — cross-source mention trends over time, convergence when independent sources land on the same story in one week, and an India lens (The Ken) connected to global agentic-AI news that almost nobody else draws.

Two consequences that constrain every design decision:

- **Never delete from `items`.** Storage is cheap; the corpus is the entire moat. Keeping raw items means re-scoring with a better prompt in a month without re-fetching.
- **Clustering is load-bearing, not a nice-to-have.** It is what replaces personal experience as the source of edge. A cluster of one is a news item. A cluster of four across independent sources is a trend, and a trend is postable.

## Pipeline

```
  ┌─ gmail ──┐
  ├─ reddit ─┤──► normalize ──► dedupe ──► cluster ──► score ──► rank ──► seeds[]
  └─ rss ────┘                     │          │          │
                                   │          │          ├─ topical fit
                                   │          │          ├─ novelty vs corpus
                                   │          │          └─ corroboration (cluster size)
                                   │          └─ group items across sources
                                   └─ vs `seen` + already-posted
```

`cluster` groups items from different sources covering the same underlying story. This is where embeddings earn their place — sentence-transformers locally, no per-item API call.

Three scoring signals, not two:

| Signal | What it catches |
|---|---|
| Topical fit | Is this agentic AI at all? Filters the ~70% of the inbox that is Nifty and Zerodha. |
| Novelty vs corpus | Have we seen this story? Have we already posted on it? The old pipeline repeated itself constantly; this is the fix. |
| Corroboration | How many independent sources? Drives cluster-based angles and filters single-source hype. |

## Invariants

- **`fetch` fans out in parallel and tolerates partial failure.** If Reddit 500s, the run completes with RSS and logs the gap. A harvest that returns empty because one source blipped is a harvest that gets turned off within a week. Never let one source's failure abort the run.
- **`fact_gate` flags, it never silently fixes.** Its job is checking that every assertion in a draft is traceable to a fetched item. When summarising AI news the real failure mode is an invented benchmark number or a launch attributed to the wrong company.
- **Dedupe runs against `seen` *and* already-posted**, not just `seen`.
- **Newsletter extraction is per-sender.** The Batch and ByteByteGo are structurally different HTML; a generic strip-the-tags pass yields navigation links and unsubscribe footers as "content."

## Storage

SQLite.

```
items    -- everything ever fetched, never deleted. this is the asset.
seen     -- dedupe keys
clusters -- item groupings + cluster metadata
seeds    -- scored, ranked, shortlisted
posts    -- urn, text, format, source_item_ids, published_at
```

## Sources

Build order is decided: **Reddit + RSS first**, Gmail newsletters in phase 2. The zero-auth sources are structured and working today, and eight independent feeds is already enough for corroboration scoring to mean something. Gmail is deferred because six hand-written per-sender parsers before the pipeline shape is settled is the wrong first week — not because the newsletters don't matter. They do; The Ken in particular carries the India angle.

| Source | Mechanism | Auth | Phase |
|---|---|---|---|
| r/AI_Agents, r/LocalLLaMA, r/LangChain, r/ClaudeAI | Apify actor | none | 1 |
| LangChain changelog, Anthropic + OpenAI engineering blogs, arXiv cs.AI agents feed | RSS | none | 1 |
| The Batch, ByteByteGo, The Ken (Zero Shot), There's An AI For That, The Pulse, IBM AI | Gmail API, desktop OAuth flow, token cached | one browser consent, once | 2 |

Gmail goes through the Gmail API with a cached token, **not** the Gmail MCP — this runs on a timer and MCP auth is not reliable in that context.

## Cadence

Daily, early morning, ahead of the 08:00 IST posting slot.

## Commands

None yet. Add build, test, single-test, and harvest-run invocations here as they exist.
