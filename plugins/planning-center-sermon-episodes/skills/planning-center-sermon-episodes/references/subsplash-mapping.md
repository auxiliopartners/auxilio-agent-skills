# Subsplash to Planning Center Field Mapping

This reference documents how to map Subsplash media export JSON to Planning Center episode fields.

**Important**: Subsplash CDN URLs will not be available after migration. Files must be downloaded locally before uploading to Planning Center.

## Subsplash JSON Structure

```json
{
  "title": "Episode Title",
  "subtitle": "Speaker Name",
  "additional_label": "Scripture Reference",
  "date": "2006-09-10T00:00:00Z",
  "slug": "url-slug",
  "_embedded": {
    "media-series": {
      "title": "Series Name",
      "id": "uuid"
    },
    "images": [
      {
        "type": "wide|square",
        "_links": {
          "related": { "href": "https://cdn.subsplash.com/..." }
        }
      }
    ],
    "audio": {
      "title": "original-filename.mp3",
      "_embedded": {
        "audio-outputs": [
          {
            "_links": {
              "related": { "href": "https://cdn.subsplash.com/...audio.m4a" }
            }
          }
        ]
      }
    }
  }
}
```

## Field Mapping Table

| Subsplash Path | Planning Center Field | Notes |
|----------------|----------------------|-------|
| `title` | Episode Title | Direct mapping |
| `subtitle` | Speaker | Search/create in People |
| `additional_label` | Description | Scripture reference (e.g., "Psalm 103") |
| `date` | Publish Date | Parse ISO 8601 format |
| `slug` | (file organization) | Use for local folder naming |
| `_embedded.media-series.title` | Series | Must exist or be created first |
| `_embedded.audio.title` | (reference) | Original audio filename |

## Recommended Local File Organization

Before uploading, organize downloaded files to match metadata:

```
sermons/
├── {slug}/                     # Use slug from JSON
│   ├── metadata.json           # The Subsplash export
│   ├── audio.mp3               # Downloaded audio file
│   └── artwork.jpg             # Downloaded artwork (square preferred)
```

Example:
```
sermons/
├── tender-mercies/
│   ├── metadata.json
│   ├── audio.mp3
│   └── artwork.jpg
├── finding-hope/
│   ├── metadata.json
│   ├── audio.mp3
│   └── artwork.jpg
```

## Extraction Functions

### Get Episode Title
```javascript
const title = data.title;
```

### Get Speaker Name
```javascript
const speaker = data.subtitle;
```

### Get Publish Date
```javascript
const date = new Date(data.date);
const publishDate = date.toLocaleDateString('en-US', {
  year: 'numeric', month: 'long', day: 'numeric'
});
// Result: "September 10, 2006"
```

### Get Series Name
```javascript
const series = data._embedded?.["media-series"]?.title;
```

### Get Slug (for file organization)
```javascript
const slug = data.slug;
// Use to name local folder: `sermons/${slug}/`
```

### Build Description
```javascript
const description = data.additional_label || "";
// e.g., "Psalm 103"
```

## Complete Transformation (with local file paths)

```javascript
function subsplashToPlanningCenter(data, basePath) {
  const slug = data.slug;
  const localPath = `${basePath}/${slug}`;

  return {
    title: data.title,
    description: data.additional_label || "",
    speaker: data.subtitle,
    series: data._embedded?.["media-series"]?.title,
    publishDate: data.date,
    // Local file paths - files must be downloaded first
    artwork: `${localPath}/artwork.jpg`,
    audioFile: `${localPath}/audio.mp3`
  };
}
```

## Pre-Migration Checklist

Before starting batch upload to Planning Center:

### 1. Download All Files from Subsplash
For each episode, download:
- Audio file (M4A or MP3)
- Artwork image (prefer square type)

### 2. Organize Files Locally
Use the slug from each metadata.json to create folder structure.

### 3. Extract Unique Series
```javascript
const allSeries = new Set();
episodes.forEach(ep => {
  const series = ep._embedded?.["media-series"]?.title;
  if (series) allSeries.add(series);
});
// Create these series in Planning Center first
```

### 4. Extract Unique Speakers
```javascript
const allSpeakers = new Set();
episodes.forEach(ep => {
  if (ep.subtitle) allSpeakers.add(ep.subtitle);
});
// Verify these exist in Planning Center People
```

### 5. Validate Files Exist
```javascript
episodes.forEach(ep => {
  const path = `${basePath}/${ep.slug}`;
  // Check: audio.mp3 exists
  // Check: artwork.jpg exists
  // Log any missing files
});
```

## Batch Processing Order

1. **Create all series first** (use planning-center-series skill)
2. **Create missing speakers** in People database
3. **Process episodes** in chronological order (oldest first)
4. **Track progress** - log completed uploads to resume if interrupted
