# PathCraft

PathCraft is an AI travel planner for route discovery, scenic stops, trip pacing, fuel planning, and itinerary generation. It combines deterministic planning engines with an optional LLM-powered chat interface.

## Overview

PathCraft is designed for road-trip style planning where the best route is not always the shortest one. It balances:
- efficiency
- scenic value
- trip experience
- practical stop planning

## Core Capabilities

- Multiple route options between supported cities
- Scenic spot discovery along the selected route
- Rest-stop and overnight-stop planning
- Fuel planning based on route distance
- Day-wise itinerary generation
- Conversational trip planning through Chainlit + LangChain

## Flow

```text
+-------------------+
|   User Request    |
+---------+---------+
          |
          v
+-------------------+
|   Route Engine    |
+---------+---------+
          |
          v
+---------+---------+------------------+------------------+
|   Scenic Engine   |   Stop Planner   |   Fuel Planner   |
+---------+---------+------------------+------------------+
          |                    |                    |
          +----------+---------+---------+----------+
                     |                   |
                     v                   v
              +-------------+    +---------------+
              | Recommender |    |   Itinerary   |
              +------+------+    +-------+-------+
                     |                   |
                     +---------+---------+
                               |
                               v
                      +------------------+
                      | CLI / Chat Output |
                      +------------------+
```

## Engines

### Route Engine
- Generates route candidates between origin and destination
- Uses a preloaded city network and pathfinding logic
- Computes route distance, estimated time, and route type

### Scenic Engine
- Finds attractions near the chosen route
- Scores places using proximity, attraction type, and uniqueness
- Surfaces scenic highlights such as waterfalls, viewpoints, beaches, heritage sites, and nature spots

### Stop Planner
- Recommends rest and overnight breaks based on journey length
- Helps structure long-distance travel into manageable segments
- Adds practical stop timing to the trip flow

### Fuel Planner
- Estimates when refueling should happen along the route
- Supports fuel cost and fuel-need planning from route distance
- Adds operational guidance for longer drives

### Recommendation Engine
- Scores route options using scenic, efficiency, and experience factors
- Ranks routes based on preferences such as scenic bias or toll avoidance
- Produces the recommended route used for the final plan

### Itinerary Generator
- Converts the recommended route into a day-wise travel plan
- Adds activities, stop timing, overnight stays, and budget estimates
- Produces a structured itinerary suitable for CLI or chat responses

## Requirements

- Python 3.9+
- `pip`
- Optional: an OpenAI-compatible LLM endpoint for chatbot mode

## Installation

```bash
python -m pip install -r requirements.txt
```

## Run The CLI

Basic usage:

```bash
python planner.py "Bangalore to Goa"
```

Prefer scenic routes:

```bash
python planner.py "Bangalore to Goa" --prefer-scenic
```

Avoid toll roads:

```bash
python planner.py "Bangalore to Goa" --avoid-tolls
```

JSON output:

```bash
python planner.py "Bangalore to Goa" --json
```

## Run The Chat UI

1. Create your environment file:

```bash
copy .env.example .env
```

2. Fill in these values in `.env`:

- `OPENCHATAI_API_KEY`
- `OPENCHATAI_BASE_URL`
- `OPENCHATAI_MODEL`
- `OPENCHATAI_TEMPERATURE`
- `OPENCHATAI_MAX_TOKENS`
- `CHAINLIT_AUTH_SECRET`

1. Start Chainlit:

```bash
chainlit run src/pathcraft/app.py
```

## Authentication Setup

PathCraft supports password-based authentication for securing your travel planning interface.

### 🔐 **Setting Up Authentication**

1. **Generate Authentication Secret:**

```bash
chainlit create-secret
```

2. **Add Secret to Environment:**

Add the generated secret to your `.env` file:

```bash
CHAINLIT_AUTH_SECRET=your_generated_secret_here
```

3. **Restart Chainlit:**

```bash
chainlit run src/pathcraft/app.py
```

### 🎯 **Authentication Features:**

- **🔒 Password Protection** - Secure access to PathCraft interface
- **👥 User Management** - Admin/user role support
- **🔄 Session Management** - Persistent login state
- **🛡️ Security** - Encrypted authentication tokens

### 📋 Default Credentials

- **Username:** `admin`
- **Password:** `admin`

*⚠️ **Security Note:** Change default credentials in production by modifying the `auth_callback` function in `app.py`*

If you prefer OpenAI-style variable names, these are also supported:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

## Example Commands

```bash
python planner.py "Mysore to Coorg"
python planner.py "Bangalore to Goa" --prefer-scenic
python planner.py "Bangalore to Goa" --avoid-tolls --json
chainlit run app.py -w
```

## Example Output

```text
PATHCRAFT RESULTS
============================================================

Route: bangalore -> goa
Total Distance: 725 km
Estimated Time: 13.18 hours
Scenic Score: 0.0/10

RECOMMENDED ROUTE HIGHLIGHTS:
  1. Belur Halebidu
  2. Mullayanagiri Peak
  3. Kudremukh Peak
```

## Notes

- The CLI works without an LLM.
- The Chainlit chat interface requires valid LLM credentials.
- The planner is only as good as the built-in route and attraction dataset for supported locations.
