---
name: planning-center-sermon-series
description: |
  Create sermon series in Planning Center Publishing within a specific channel.
  TRIGGERS: "create series", "add series", "new sermon series", "Planning Center series",
  "upload series", "batch series", mentions of sermon series with artwork/images.
  Use when user wants to create one or more series with title, description, and artwork.
---

# Planning Center Series Creation

Create sermon series using browser automation (Claude in Chrome). API is used for metadata where possible; browser automation handles artwork uploads.

## Prerequisites

- User logged into Planning Center Publishing in Chrome
- Claude in Chrome extension active
- Target channel must exist

## Workflow Overview

1. Get browser context → `tabs_context_mcp`
2. Navigate to channel's Series tab
3. Click "Add series"
4. Fill metadata (title, description)
5. Upload artwork via image picker
6. Save and verify

## Single Series Creation

### Step 1: Navigate to Channel

```
URL pattern: https://publishing.planningcenteronline.com/sermons/channels/{channel_id}
Click "Series" tab in channel navigation
```

### Step 2: Create Series

1. Find and click "Add series" button:
   ```
   find query: "Add series button"
   left_click on ref
   ```

2. Fill title field:
   ```
   find query: "Title input"
   form_input with value: "{series_title}"
   ```

3. Fill description:
   ```
   find query: "description textarea"
   form_input with value: "{series_description}"
   ```

### Step 3: Upload Artwork

1. Click series image edit button:
   ```
   find query: "Edit series image pencil"
   left_click on ref
   ```

2. In "Choose image" modal, click browse or use upload:
   ```
   find query: "Choose image"
   left_click → opens modal
   find query: "browse" link
   upload_image with ref and imageId from user's file
   ```

3. Confirm with "Add image" button

### Step 4: Save

Series auto-saves on field change, but verify by checking for success indicators or taking screenshot.

## Batch Creation

For multiple series from JSON array:

```javascript
// Expected input format
[
  {
    "title": "Faith Over Fear",
    "description": "A 4-week series on trusting God...",
    "artwork": "/path/to/faith-over-fear.jpg"
  },
  {
    "title": "Kingdom Come",
    "description": "Exploring the Lord's Prayer...",
    "artwork": "/path/to/kingdom-come.jpg"
  }
]
```

Process each series sequentially:
1. Create series with metadata
2. Upload artwork
3. Screenshot to verify
4. Continue to next series
5. Report summary when complete

## Element References

| Element | Find Query | Action |
|---------|------------|--------|
| Add Series | "Add series button" | left_click |
| Title | "Title input" or "Series title" | form_input |
| Description | "description textarea" | form_input |
| Image Edit | "Edit series image" | left_click |
| Browse | "browse" in modal | left_click or upload_image |
| Add Image | "Add image button" | left_click |

## Error Handling

- **Element not found**: Take screenshot, retry with alternate query
- **Upload timeout**: Retry up to 3 times with 5s delay
- **Session expired**: Notify user to re-authenticate
- **Duplicate title**: Warn user, ask whether to skip or rename
