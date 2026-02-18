---
name: planning-center-sermon-episodes
description: |
  Create sermon episodes in Planning Center Publishing within a series.
  TRIGGERS: "create episode", "add episode", "upload sermon", "upload episode",
  "batch upload sermons", "Planning Center episode", "sermon upload", "audio upload to Planning Center",
  "Subsplash import", "migrate from Subsplash".
  Use when user wants to create episodes with: title, description, artwork, audio file,
  video URL, publish date/time, and speaker assignment. Handles speaker lookup/creation in People database.
  Supports Subsplash JSON export format for migration.
---

# Planning Center Episode Creation

Create sermon episodes using browser automation (Claude in Chrome) for all UI interactions including file uploads.

## Prerequisites

- User logged into Planning Center Publishing in Chrome
- Claude in Chrome extension active
- Target series must exist within a channel
- Audio and artwork files accessible locally
- Speaker names must match or be creatable in People database

## Workflow Overview

1. Get browser context → `tabs_context_mcp`
2. Navigate to target channel → Episodes tab
3. Click "Add episode"
4. Fill General tab (title, summary, series, speaker, dates)
5. Upload episode artwork
6. Go to Media tab → upload audio file
7. Screenshot to verify, then proceed to next

## Episode Data Structure

### Standard Format
```json
{
  "title": "Finding Peace in the Storm",
  "description": "Matthew 8:23-27",
  "series": "Faith Over Fear",
  "speaker": "John Smith",
  "publishDate": "2024-03-10",
  "publishTime": "09:00",
  "artwork": "/path/to/episode-art.jpg",
  "audioFile": "/path/to/sermon.mp3",
  "videoUrl": "https://youtube.com/watch?v=..."
}
```

### Subsplash Export Format

For Subsplash JSON imports, see [references/subsplash-mapping.md](references/subsplash-mapping.md) for field mapping.

Key Subsplash → Planning Center mappings:
- `title` → Episode Title
- `subtitle` → Speaker Name
- `additional_label` → Description (scripture reference)
- `date` → Publish Date
- `_embedded.media-series.title` → Series

**File Organization for Subsplash Migration**:
Ensure local files are organized to match metadata. Recommended structure:
```
sermons/
├── 2006-09-10-tender-mercies/
│   ├── metadata.json
│   ├── audio.mp3 (or audio.m4a)
│   └── artwork.jpg
├── 2006-09-17-next-sermon/
│   ├── metadata.json
│   ├── audio.mp3
│   └── artwork.jpg
```

## Single Episode Creation

### Step 1: Navigate to Channel

```
Navigate to: https://publishing.planningcenteronline.com/sermons/channels/{channel_id}
Click "Episodes" tab (if not already there)
Click "Add episode" button
```

### Step 2: Fill General Tab

1. **Title** (required):
   ```
   find: "Title input"
   form_input: "{episode_title}"
   ```

2. **Summary**:
   ```
   find: "Add a summary" or "summary textarea"
   form_input: "{description}"
   ```

3. **Series** (dropdown):
   ```
   find: "Select a series" combobox
   left_click → opens dropdown
   find: "{series_name}" option
   left_click to select
   ```

4. **Speaker** (search field):
   ```
   find: "Add Episode speaker"
   form_input: "{speaker_name}"
   Wait for autocomplete results
   If found → click to select
   If not found → see "Speaker Creation" section
   ```

5. **Publish Date/Time**:
   ```
   find: "Episode publish date"
   form_input: "{date}" (format: March 10, 2024)
   find: "Hours" / "Minutes" / "AM/PM" inputs
   form_input for each time component
   ```

### Step 3: Upload Artwork

1. Click episode image edit:
   ```
   find: "Edit episode image"
   left_click
   ```

2. In "Choose image" modal:
   ```
   find: "browse" link in modal
   upload_image with ref parameter pointing to file input
   ```

3. After image appears in preview:
   ```
   find: "Add image" button
   left_click
   ```

4. Wait for modal to close and thumbnail to update

### Step 4: Upload Audio (Media Tab)

1. Navigate to Media tab:
   ```
   find: "Media and resources" tab link
   left_click
   ```

2. Scroll to "On-demand settings" → "Audio on-demand library"

3. Upload audio file:
   ```
   find: "Choose file" button (type=file) under Audio section
   upload_image with ref and local audio file path
   ```

4. **Wait for upload to complete** - this is the slowest step:
   - Small files (~10MB): 15-30 seconds
   - Medium files (~30MB): 45-90 seconds
   - Large files (~60MB+): 90-180 seconds
   - Watch for progress indicator or "Save" button becoming active

5. Save audio:
   ```
   find: "Save" button near audio section
   left_click
   ```

### Step 5: Add Video URL (Optional)

In Media tab, under "Video on-demand library":
```
find: "Video on-demand library" textarea
form_input: "{video_url}"
find: "Save" near video section
left_click
```

### Step 6: Verify and Continue

Take screenshot to verify episode was created correctly, then navigate back to Episodes list for next upload.

## Speaker Handling

### Lookup Existing Speaker

1. Type speaker name in speaker field
2. Wait 1-2 seconds for autocomplete
3. If results appear, click matching name

### Create New Speaker

If speaker not found in autocomplete:

1. Open new tab, navigate to People:
   ```
   URL: https://people.planningcenteronline.com/people
   ```

2. Click "New person" or equivalent

3. Fill required fields:
   - First name
   - Last name

4. Save person

5. Return to episode tab and search for speaker again

## Batch Episode Upload

### Pre-Processing Steps (Critical for Large Batches)

Before starting batch upload:

1. **Extract unique series** from all metadata files
2. **Create all series first** using planning-center-series skill
3. **Extract unique speakers** and verify they exist in People
4. **Create missing speakers** before starting episode uploads
5. **Validate all files exist** - check each audio and artwork file is accessible

### Subsplash Batch Import

```javascript
// Transform Subsplash JSON to standard format
function transformSubsplash(data, localFilesPath) {
  return {
    title: data.title,
    description: data.additional_label || "",
    speaker: data.subtitle,
    series: data._embedded?.["media-series"]?.title,
    publishDate: data.date,
    // Local file paths (files must be downloaded from Subsplash first)
    artwork: `${localFilesPath}/artwork.jpg`,
    audioFile: `${localFilesPath}/audio.mp3`
  };
}
```

### Batch Processing Strategy

For 1000 episodes, process in manageable batches:

1. **Batch size**: 20-50 episodes per session
2. **Session breaks**: Re-verify login every 50 episodes
3. **Progress tracking**: Log completed episodes to resume if interrupted
4. **Error handling**: Skip failed episodes, log for retry later

### Batch Processing Loop

```
For each episode in batch:
  1. Navigate to channel episodes list
  2. Click "Add episode"
  3. Fill metadata (title, summary, series, speaker, date)
  4. Upload artwork
  5. Switch to Media tab
  6. Upload audio file (wait for completion!)
  7. Screenshot to verify
  8. Log success
  9. Continue to next episode
```

## Element Reference Table

| Element | Find Query | Tab | Action |
|---------|------------|-----|--------|
| Add Episode | "Add episode button" | Episodes list | left_click |
| Title | "Title input" | General | form_input |
| Summary | "Add a summary" | General | form_input |
| Series | "Select a series" | General | click + select |
| Speaker | "Add Episode speaker" | General | form_input + select |
| Publish Date | "Episode publish date" | General | form_input |
| Episode Image | "Edit episode image" | General | left_click |
| Browse (image) | "browse" in modal | Image modal | upload_image |
| Add Image | "Add image" button | Image modal | left_click |
| Media Tab | "Media and resources" | Nav tabs | left_click |
| Audio Upload | "Choose file" under Audio | Media | upload_image |
| Audio Save | "Save" near audio | Media | left_click |
| Video URL | "Video on-demand" | Media | form_input |

## Error Handling

| Error | Detection | Recovery |
|-------|-----------|----------|
| Speaker not found | No autocomplete results | Create person in People, retry |
| Upload timeout | No progress after 180s | Retry upload up to 3 times |
| Session expired | Login page appears | Notify user to re-login |
| Series not found | Dropdown empty/no match | Create series first |
| File not found | Upload fails immediately | Check file path, skip episode |
| Duplicate episode | Warning message | Skip or rename with date suffix |

## Time Estimates (File Upload Method)

| Operation | Time |
|-----------|------|
| Navigate + create episode | 3-5 seconds |
| Fill metadata fields | 15-20 seconds |
| Upload artwork (~1MB) | 10-20 seconds |
| Upload audio (~30MB) | 60-90 seconds |
| Upload audio (~60MB) | 90-180 seconds |
| Verify + navigate back | 5-10 seconds |
| **Total per episode** | **~2-4 minutes** |

### Batch Time Projections

| Episodes | Estimated Time | Notes |
|----------|---------------|-------|
| 10 | 30-45 minutes | Good for testing |
| 50 | 2-3 hours | One session |
| 100 | 4-7 hours | Break into 2 sessions |
| 500 | 20-35 hours | Multiple days |
| 1000 | 40-70 hours | Plan for 1-2 weeks |

**Optimization tip**: Run uploads during off-peak hours for faster network speeds.
