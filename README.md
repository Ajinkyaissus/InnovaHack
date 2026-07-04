# AEGIS — Frontend Integration Guide

This is a static, self-contained frontend prototype (`aegis-redesign-animated.html`).
There is **no backend wired in** — every case shown on screen currently comes from a
hardcoded `fixtures` object in the `<script>` block, and "processing" is a timed
animation, not a real pipeline. This doc covers what to change to connect it to a
real backend, and how to turn off the built-in demo tooling.

## 1. Turning off demo mode

The file ships with a **Scenario Loader** panel (buttons like "Clean Case",
"Ambiguous Entity", "OCR Failed", etc.) used for previewing the 7 mock case states.

- It's **hidden by default**. It only appears if the page is loaded with
  `?demo=true` in the URL (e.g. `https://yourapp.com/?demo=true`).
- The toggle logic lives near the bottom of the `<script>` block:

  ```js
  const scenarioPanel = document.getElementById('scenario-loader-panel');
  if (scenarioPanel && new URLSearchParams(window.location.search).get('demo') !== 'true') {
    scenarioPanel.style.display = 'none';
  }
  ```

- **Once the real backend is wired in**, delete entirely rather than just hide:
  - The `#scenario-loader-panel` `<div>` in the HTML (search for `id="scenario-loader-panel"`)
  - The `fixtures` object
  - The `loadFixture(key)` function
  - The toggle snippet above

  Leaving fixture data or the loader in a shipped build risks a client-facing user
  triggering fake case data.

## 2. What the frontend currently does instead of calling a backend

All three integration points are marked in the code with `// TODO(backend):` comments
so they're easy to find with a search.

### a) File upload (`handleFileSelect`, `handleFiles`)

Right now, selected files are read into a local `selectedFiles` array and just
rendered as a file list — **nothing is sent anywhere**. This is where you'll add
the real upload request, e.g.:

```js
async function uploadFiles(files) {
  const formData = new FormData();
  files.forEach(f => formData.append('documents', f));

  const res = await fetch('/api/cases', { method: 'POST', body: formData });
  if (!res.ok) throw new Error('Upload failed');
  return res.json(); // should return something you can use to start polling, e.g. { caseId }
}
```

Call this from `startProcessing()` before/instead of jumping straight into the fake
progress animation.

### b) Processing / progress (`runProcessingSteps`)

Currently a fixed-timing loop that advances through `['ocr', 'extraction',
'validation', 'evidence', 'summary']` using `setTimeout`, regardless of whether
anything real happened. Replace this with either:

- **Polling**: hit a status endpoint (e.g. `GET /api/cases/:id/status`) every
  1–2 seconds and update `markActive(idx)` / mark steps done based on the real
  stage the backend reports, or
- **WebSocket / SSE**: push stage updates from the server as they happen.

Either way, once the backend reports the case is fully processed, call
`renderCaseBoard(data)` with the real case payload (see the data contract below)
instead of `showCaseBoard()` pulling from `fixtures`.

### c) Case data (`fixtures` object → real API response)

`renderCaseBoard(data)` is the single function that draws everything: title, ID,
recommendation badge, document tags, extracted fields, validation checklist,
evidence panel, and draft message. It expects a JS object of this shape:

```ts
{
  id: string;                // e.g. "CASE-001"
  title: string;             // shipper/entity name shown as the case heading
  documents: Array<{
    id: string;
    name: string;             // filename shown as a tag
    type: 'invoice' | 'origin' | 'packing' | 'bill' | string;
  }>;
  fields: Array<{
    id: string;
    label: string;
    value: string;            // use 'NOT_FOUND' if extraction failed for this field
    confidence: number;        // 0–1
    status: 'verified' | 'needs_review' | 'unable_to_verify';
    suggestion?: string;       // shown when status needs a suggested correction
  }>;
  validationRules: Array<{
    id: string;
    name: string;
    detail: string;
    status: 'passed' | 'failed';
  }>;
  evidence: {
    type: 'match' | 'ambiguous' | 'error';
    sourceCount?: number;
    confidenceLabel?: string;
    candidates?: Array<{ name: string; country: string; confidence: number; sourceCount: number }>;
    negativeNewsFlag?: boolean;
    summary?: string;
    error?: 'ocr_failed' | 'evidence_timeout';   // only when type is 'error'
  };
  summary: {
    text: string;
    recommendation: 'approve' | 'further_investigation_recommended' | 'additional_documents_required';
    badgeLabel: string;
    draft: string;             // pre-filled draft message text, can be empty string
  };
  synthesis: Array<{ doc: string; weight: string; value: string }>;  // only used for multi-document cases, otherwise []
}
```

**Keep these field names and status enum values exact** unless you also update
the corresponding render logic in `renderCaseBoard()` — the UI branches directly
on strings like `'approve'`, `'ocr_failed'`, `'needs_review'`, etc.

To push a real case into the UI once you have data in this shape:

```js
currentCaseData = realCaseDataFromApi;
renderCaseBoard(currentCaseData);
```

## 3. Suggested minimal API surface

This is a suggestion, not a requirement — adapt to whatever your backend already does.

| Endpoint | Purpose |
|---|---|
| `POST /api/cases` | Upload documents, returns `{ caseId }` (or the full case object if processing is synchronous) |
| `GET /api/cases/:id/status` | Poll processing stage (`ocr`, `extraction`, `validation`, `evidence`, `summary`, `done`) |
| `GET /api/cases/:id` | Fetch the completed case object (shape above) |
| `PATCH /api/cases/:id/fields/:fieldId` | Save a manual field correction (used by "Save & Continue" / field correction flows) |
| `POST /api/cases/:id/candidate` | Confirm the selected entity when `evidence.type === 'ambiguous'` |

## 4. Pre-launch checklist

- [ ] Remove `#scenario-loader-panel`, `fixtures`, `loadFixture()`, and the demo-flag toggle
- [ ] Wire `handleFileSelect`/`handleFiles` to a real upload request
- [ ] Replace `runProcessingSteps()`'s fake timers with real status polling/streaming
- [ ] Confirm your backend's response shape matches the contract in Section 2c (or update `renderCaseBoard` to match)
- [ ] Wire up field-correction, reconstruction, and candidate-selection actions
  (`saveFieldCorrection`, `confirmReconstruction`, `selectCandidate`,
  `confirmActiveCandidate`) to real save endpoints — they currently only mutate
  local state
- [ ] Wire `copyDraft()` / `regenerateDraft()` to a real draft-generation endpoint if the message text should be dynamic rather than pulled from `summary.draft`
