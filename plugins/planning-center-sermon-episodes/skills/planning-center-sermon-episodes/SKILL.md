---
name: planning-center-sermon-episodes
description: |
  Create and update sermon episodes in Planning Center Publishing within a series.
  TRIGGERS: "create episode", "add episode", "upload sermon", "upload episode",
  "batch upload sermons", "Planning Center episode", "sermon upload", "audio upload to Planning Center",
  "Subsplash import", "migrate from Subsplash", "set episode date", "set publish date",
  "assign speaker", "update episode", "pending uploads", "finish episodes", "episode date and speaker".
  Use when user wants to create episodes with: title, description, artwork, audio file,
  video URL, publish date/time, and speaker assignment. Also handles updating existing episodes
  to set publish dates and assign speakers via browser automation (required because the PCO API
  returns 422 Forbidden for date fields and speaker assignment endpoints).
  Integrates with CLI progress tracking via `yarn pending-uploads` and `yarn mark-done`.
  Supports Subsplash JSON export format for migration.
---

# Planning Center Episode Upload & Update

Upload artwork/audio, set date/speaker, and remove live times on existing sermon episodes using browser automation (Claude in Chrome).

## Prerequisites

- User logged into Planning Center Publishing in Chrome
- Claude in Chrome extension active
- Episode records already created via `yarn migrate` (they have PCO IDs)
- CDN URLs for artwork and audio available via `yarn pending-uploads`

## Getting Episode Data

Run `yarn pending-uploads` to get episodes needing work:

```json
{
  "type": "episode",
  "slug": "2006-06-03-philemons-problem-and-ours",
  "episodeId": "618527",
  "title": "Philemon's Problem and Ours",
  "speakerNames": ["Rankin Wilbourne"],
  "speakerPeopleIds": ["1272319"],
  "publishDate": "2006-06-03T00:00:00Z",
  "artworkUrl": "https://cdn.subsplash.com/images/.../image.jpg",
  "audioUrl": "https://cdn.subsplash.com/audios/.../audio.m4a",
  "steps": ["artwork_uploaded", "audio_uploaded", "speaker_assigned", "date_set", "live_time_removed"]
}
```

## Critical: File Upload via JavaScript

**Do NOT use `upload_image` with ref** — it doesn't work with CDN URLs. Use JS fetch + DataTransfer:

```javascript
(async () => {
  const response = await fetch('{url}');
  const blob = await response.blob();
  const file = new File([blob], '{filename}', { type: '{mimeType}' });
  const dt = new DataTransfer();
  dt.items.add(file);
  const input = document.querySelector('{inputSelector}');
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
  return `Uploaded (${(blob.size / 1024 / 1024).toFixed(1)} MB)`;
})()
```

## Speed Guidelines

- **Do NOT screenshot after every action.** Only screenshot at milestones (after artwork+audio done, after date+speaker+live-time done).
- **Do NOT wait between actions** unless a modal or upload progress requires it.
- **Batch mark-done commands** — run all applicable ones together after verifying a milestone.
- **Combine date + speaker + live-time removal** in one page visit with a single Save before live-time removal.

## Workflow: Process Each Episode

### 1. Navigate to Episode Edit Page

```
https://publishing.planningcenteronline.com/sermons/episodes/{episodeId}/edit
```

### 2. Upload Artwork (if `artwork_uploaded` in steps)

Execute these actions in rapid sequence — no screenshots between:

1. Click the pencil icon on the episode image to open the inline modal. **Note:** `find: "Edit episode image"` may only hover rather than click — if the modal doesn't open, click directly by coordinate on the pencil icon (bottom-left of the image thumbnail, approximately `[39, 176]`).
2. `find: "Choose image"` → `left_click` (this creates the file input — it doesn't exist until clicked)
3. Run JS to inject artwork:
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

### 3. Upload Audio (if `audio_uploaded` in steps)

1. `find: "Media and resources"` tab → `left_click`
2. `find: "Audio on-demand library"` → `scroll_to`
3. Run JS to inject audio:
   ```javascript
   (async () => {
     const response = await fetch('{audioUrl}');
     const blob = await response.blob();
     const isM4a = '{audioUrl}'.endsWith('.m4a');
     const file = new File([blob], isM4a ? 'audio.m4a' : 'audio.mp3', { type: isM4a ? 'audio/mp4' : 'audio/mpeg' });
     const dt = new DataTransfer();
     dt.items.add(file);
     const inputs = document.querySelectorAll('input[type="file"]');
     const audioInput = inputs[inputs.length - 1];
     audioInput.files = dt.files;
     audioInput.dispatchEvent(new Event('change', { bubbles: true }));
     return `Audio: ${(blob.size / 1024 / 1024).toFixed(1)} MB`;
   })()
   ```
4. Wait ~3s for upload indicator. Audio auto-saves (no Save button needed).

**MILESTONE: Screenshot to confirm artwork thumbnail + audio attached.** Then run:
```bash
yarn mark-done --episode {slug} --step artwork_uploaded && yarn mark-done --episode {slug} --step audio_uploaded
```

### 4. Set Date + Speaker + Remove Live Time

Navigate back to General tab if on Media tab. Do all three in one pass:

**Set publish date** (if `date_set` in steps):
- Parse `publishDate` (e.g., `2006-06-03T00:00:00Z` → June 3, 2006)
- `find: "Episode publish date"` → `triple_click` to select → `type: "June 3, 2006"`
- `find: "Hours"` → `triple_click` → `type: "10"` (form_input doesn't reliably set this field)
- `find: "Minutes"` → `triple_click` → `type: "00"`
- Ensure AM/PM is set to "AM"

**Assign speaker** (if `speaker_assigned` in steps):
- `find: "Add Episode speaker"` → `form_input: "{speakerName}"`
- Wait ~1s for autocomplete → `find` matching name in dropdown → `left_click`

**The form auto-saves** — no explicit Save button is needed.

**Remove live time** (if `live_time_removed` in steps):
- **IMPORTANT**: Override confirm dialog first to prevent Chrome extension disconnection:
  ```javascript
  window.confirm = () => true;
  ```
- `find: "Remove time"` → `left_click`
- The live time entry disappears automatically.

**MILESTONE: Screenshot to confirm date, speaker, and empty live times.** Then run:
```bash
yarn mark-done --episode {slug} --step date_set && yarn mark-done --episode {slug} --step speaker_assigned && yarn mark-done --episode {slug} --step live_time_removed
```

When all 5 steps are marked done, the episode status automatically promotes to `completed`.

## Batch Processing Loop

```
1. Run: yarn pending-uploads
2. For each episode:
   a. Navigate to /sermons/episodes/{episodeId}/edit
   b. Upload artwork + audio (steps 2-3), screenshot, mark-done
   c. Set date + speaker + remove live time (step 4), screenshot, mark-done
   d. Continue to next episode
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Speaker not found in autocomplete | Create person in People first, retry |
| Upload timeout (no progress 180s) | Retry up to 3 times |
| Session expired (login page) | Notify user to re-login |
| CDN fetch fails | Check URL, retry |
| File input not found | Take screenshot, find correct selector |
| Confirm dialog blocks extension | Run `window.confirm = () => true` before clicking Remove time |
