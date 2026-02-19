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

## File Upload Technique (Critical)

**Do NOT use `upload_image` with ref** — it does not work with CDN URLs. Instead, use JavaScript to fetch the file from its CDN URL and inject it into the file input via the DataTransfer API.

Use `mcp__claude-in-chrome__javascript_tool` to execute this code in the browser tab.

## Workflow: Upload Series Artwork

### Step 1: Navigate to Series Edit Page

Navigate to the channel's series list, then find and click into the target series:
```
URL: https://publishing.planningcenteronline.com/sermons/channels/{channel_id}
Click "Series" tab
Find and click the series by title
```

### Step 2: Upload Artwork

1. Click the series image edit button:
   ```
   find: "Edit series image" or pencil icon on the image
   left_click
   ```

2. Wait for the "Choose image" modal to appear.

3. Use JavaScript to fetch the artwork from the CDN URL and inject it into the file input:
   ```javascript
   // Execute via javascript_tool in the browser tab
   (async () => {
     const url = '{artworkUrl}';  // from pending-uploads output
     const response = await fetch(url);
     const blob = await response.blob();
     const file = new File([blob], 'artwork.jpg', { type: 'image/jpeg' });
     const dt = new DataTransfer();
     dt.items.add(file);
     const input = document.querySelector('input[type="file"]');
     input.files = dt.files;
     input.dispatchEvent(new Event('change', { bubbles: true }));
     return `Uploaded artwork (${(blob.size / 1024 / 1024).toFixed(1)} MB)`;
   })()
   ```

4. Wait for the image preview to appear in the modal.

5. Click "Add image" button to confirm:
   ```
   find: "Add image" button
   left_click
   ```

6. Wait for modal to close and thumbnail to update.

### Step 3: Mark Complete

```bash
yarn mark-done --series "Series Title" --step artwork
```

## Batch Processing

```
1. Run: yarn pending-uploads
2. Filter items where type === "series"
3. For each series:
   a. Navigate to series page
   b. Upload artwork via JS fetch+DataTransfer
   c. Run: yarn mark-done --series "{title}" --step artwork
   d. Screenshot to verify
   e. Continue to next series
```

## Element References

| Element | Find Query | Action |
|---------|------------|--------|
| Series Tab | "Series" tab | left_click |
| Series Link | series title text | left_click |
| Image Edit | "Edit series image" or pencil icon | left_click |
| File Input | `input[type="file"]` in modal | JS fetch+DataTransfer |
| Add Image | "Add image" button | left_click |

## Error Handling

- **Element not found**: Take screenshot, retry with alternate query
- **CDN fetch fails**: Check URL, retry up to 3 times
- **Session expired**: Notify user to re-authenticate
- **Duplicate title**: Warn user, ask whether to skip or rename
