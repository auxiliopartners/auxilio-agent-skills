---
name: planning-center-sermon-series
description: |
  Create sermon series in Planning Center Publishing within a specific channel.
  TRIGGERS: "create series", "add series", "new sermon series", "Planning Center series",
  "upload series", "batch series", mentions of sermon series with artwork/images.
  Use when user wants to create one or more series with title, description, and artwork.
---

# Planning Center Series Artwork Upload

Upload artwork to existing sermon series using browser automation (Claude in Chrome).

## Prerequisites

- User logged into Planning Center Publishing in Chrome
- Claude in Chrome extension active
- Series records already created via `yarn migrate` (they have PCO IDs)
- Artwork CDN URLs available via `yarn pending-uploads`

## Getting Series Data

Run `yarn pending-uploads` to get series needing artwork:

```json
{
  "type": "series",
  "title": "Grace & Truth",
  "planningCenterId": "12345",
  "artworkUrl": "https://cdn.subsplash.com/images/.../image.jpg",
  "steps": ["artwork"]
}
```

## Critical: File Upload via JavaScript

**Do NOT use `upload_image` with ref** — it doesn't work with CDN URLs. Use JS fetch + DataTransfer:

```javascript
(async () => {
  const response = await fetch('{artworkUrl}');
  const blob = await response.blob();
  const file = new File([blob], 'artwork.jpg', { type: 'image/jpeg' });
  const dt = new DataTransfer();
  dt.items.add(file);
  const input = document.querySelector('input[type="file"]');
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
  return `Artwork: ${(blob.size / 1024 / 1024).toFixed(1)} MB`;
})()
```

## Speed Guidelines

- **Do NOT screenshot after every action.** Only screenshot after artwork is confirmed on the page.
- **Do NOT wait between actions** unless a modal or upload progress requires it.
- **Batch mark-done commands** when processing multiple series.

## Workflow: Upload Series Artwork

### Step 1: Navigate to Series Edit Page

Navigate directly by PCO ID — no need to search through paginated series list:
```
https://publishing.planningcenteronline.com/sermons/series/{planningCenterId}/edit
```

### Step 2: Upload Artwork

Execute these actions in rapid sequence:

1. Click the pencil icon on the series image (bottom-left of the image thumbnail, approximately `[39, 176]`).
2. An inline menu appears with "Choose image" and "Remove". Click `find: "Choose image"` → `left_click` (this opens the "Choose image" modal and creates the file input).
3. Run JS to inject artwork from CDN URL:
   ```javascript
   (async () => {
     const response = await fetch('{artworkUrl}');
     const blob = await response.blob();
     const file = new File([blob], 'artwork.jpg', { type: 'image/jpeg' });
     const dt = new DataTransfer();
     dt.items.add(file);
     const input = document.querySelector('input[type="file"]');
     input.files = dt.files;
     input.dispatchEvent(new Event('change', { bubbles: true }));
     return `Artwork: ${(blob.size / 1024 / 1024).toFixed(1)} MB`;
   })()
   ```
4. Wait ~2s for preview to render, then `find: "Add image"` → `left_click`

**MILESTONE: Screenshot to confirm artwork thumbnail updated.** Then run:
```bash
yarn mark-done --series "{title}" --step artwork
```

## Batch Processing Loop

```
1. Run: yarn pending-uploads
2. Filter items where type === "series"
3. For each series:
   a. Navigate to /sermons/series/{planningCenterId}/edit
   b. Upload artwork via pencil → Choose image → JS fetch+DataTransfer → Add image
   c. Run: yarn mark-done --series "{title}" --step artwork
   d. Continue to next series
4. Screenshot periodically to verify (not after every single series)
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Pencil icon doesn't open menu | Take screenshot, try `find: "Edit series image"` instead |
| File input not found after "Choose image" | Wait 1s, retry — input is created dynamically |
| CDN fetch fails | Check URL, retry up to 3 times |
| Session expired (login page) | Notify user to re-login |
