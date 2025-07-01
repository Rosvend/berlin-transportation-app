# Berlin Transport API Documentation (BVG)

## Overview

The BVG Transport REST API provides real-time public transportation data for Berlin. This documentation focuses on the radar endpoint used in my ELT pipeline for extracting vehicle movement data.

**Base URL:** `https://v6.bvg.transport.rest`

**Authentication:** Not required

**Rate Limits:** 
- 100 requests/minute (standard)
- 200 requests/minute (burst)

## Radar Endpoint

### `GET /radar`

The radar endpoint finds all vehicles currently in a specified geographic area along with their real-time movements. This is the primary endpoint used in my data ingestion pipeline.

**Purpose:** Extract real-time vehicle position and movement data for analysis in Snowflake.

### Required Parameters

| Parameter | Description | Type | Example |
|-----------|-------------|------|---------|
| `north` | Northern latitude boundary | number | `52.55` |
| `south` | Southern latitude boundary | number | `52.45` |
| `west` | Western longitude boundary | number | `13.35` |
| `east` | Eastern longitude boundary | number | `13.45` |

### Optional Parameters

| Parameter | Description | Type | Default | Notes |
|-----------|-------------|------|---------|--------|
| `results` | Maximum number of vehicles to return | integer | `256` | Set to `1` for testing |
| `duration` | Compute frames for next n seconds | integer | `30` | Used `60` in implementation |
| `frames` | Number of frames to compute | integer | `3` | Used `10` in implementation |
| `polylines` | Include geographic shape data | boolean | `true` | Movement path visualization |
| `language` | Response language | string | `en` | |
| `pretty` | Pretty-print JSON responses | boolean | `true` | |

## Request Examples

### Berlin City Center
```bash
curl "https://v6.bvg.transport.rest/radar?north=52.55&south=52.45&west=13.35&east=13.45&duration=60&frames=10&results=1" -s | jq
```

### Python Implementation (from departures.py)
```python
def get_radar(north, south, west, east, duration, frames, results=1, polylines=True):
    url = f"{API_URL}/radar?north={north}&south={south}&west={west}&east={east}&duration={duration}&frames={frames}&results={results}&polylines={polylines}"
    response = requests.get(url)
    return response.json()
```

## Response Structure

The API returns a JSON object or array containing vehicle movement data:

```json
{
  "movements": [
    {
      "line": {
        "name": "M10",
        "type": "tram"
      },
      "tripId": "1|123456|0|80|12345678",
      "location": {
        "latitude": 52.52411,
        "longitude": 13.41002
      },
      "direction": "Warschauer Str.",
      "realtimeDataUpdatedAt": 1640995200000
    }
  ]
}
```

### Key Response Fields

| Field | Description | Type | Notes |
|-------|-------------|------|--------|
| `movements` | Array of vehicle objects | array | Main data container |
| `line.name` | Line identifier (e.g., "M10", "U1") | string | Transport line number |
| `line.type` | Transport type | string | "tram", "bus", "subway", etc. |
| `tripId` | Unique trip identifier | string | Used for tracking specific journeys |
| `location.latitude` | Vehicle latitude | number | WGS84 coordinate |
| `location.longitude` | Vehicle longitude | number | WGS84 coordinate |
| `direction` | Destination/direction | string | Human-readable destination |
| `realtimeDataUpdatedAt` | Last update timestamp | number | Unix timestamp in milliseconds |

## Data Processing Notes

### Timestamp Conversion
The API returns timestamps in Unix milliseconds. Our pipeline converts these to UTC ISO format:

```python
def convert_to_utc(timestamp_ms):
    timestamp_seconds = timestamp_ms / 1000
    utc_datetime = datetime.fromtimestamp(timestamp_seconds, tz=pytz.UTC)
    return utc_datetime.isoformat()
```

### Geographic Boundaries (Berlin)
Common Berlin coordinate boundaries used in my pipeline:

- **North:** 52.55 (Northern districts)
- **South:** 52.45 (Southern districts)  
- **West:** 13.35 (Western districts)
- **East:** 13.45 (Eastern districts)

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `429` - Rate limit exceeded
- `500` - Internal server error

Example error handling from my implementation:
```python
if response.status_code == 200:
    return response.json()
else:
    logging.error(f"API request failed with status {response.status_code}")
    response.raise_for_status()
```

## Pipeline Integration

This endpoint feeds data into my Snowflake-based ELT pipeline:

1. **Extract:** Fetch real-time vehicle positions via radar endpoint
2. **Load:** Store raw JSON responses in Snowflake staging
3. **Transform:** Process timestamps, normalize coordinates, extract vehicle metrics

The radar data provides the foundation for analyzing Berlin's public transport patterns, delays, and coverage areas.