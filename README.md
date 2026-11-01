# Personal Journal Analysis & Automation System

An AI-powered personal journaling automation system built with **n8n, PostgreSQL, Docker, and Ollama**.

This project automates the process of analyzing daily journal entries using local Large Language Models (LLMs), extracting emotional insights, generating personalized reflections, storing structured results in a relational database, and creating organized text archives.

The main goal is to transform ordinary journal entries into structured, searchable, and meaningful personal records without requiring manual analysis.

---

## Project Overview

Writing a journal regularly can provide valuable insights into personal habits, emotions, and daily experiences. However, manually reviewing entries, identifying emotional patterns, and reflecting on each day can become time-consuming.

This project addresses that problem by building an automated pipeline that:

- Reads daily journal entries from local text files.
- Identifies the newest available journal entry.
- Analyzes its sentiment and emotional content using an LLM.
- Generates a personalized reflection based on the journal entry.
- Sends the AI-generated reflection through Telegram.
- Stores structured analytical results in PostgreSQL.
- Creates a complete text archive containing the original journal and AI-generated insights.

The workflow runs automatically on a scheduled basis.

## System Architecture

The application is organized as a sequence of automated processing stages.

```text
                  Schedule Trigger
                         |
                         v
                 Read Journal Files
                         |
                         v
                  Select Newest File
                         |
                         v
                  Extract Journal Text
                         |
                         v
                 Check PostgreSQL
                  for Duplicate File
                         |
                         v
                     IF Node
                         |
                +--------+--------+
                |                 |
             Already           Not Yet
            Processed         Processed
                |                 |
              Skip                v
                         Sentiment Analysis
                                  |
                                  v
                          Parse JSON Output
                                  |
                                  v
                           AI Reflection
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
               Telegram                  PostgreSQL
               Notification               Insert Data
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                            Prepare Archive
                                  |
                                  v
                           Format Text Report
                                  |
                                  v
                           Convert to File
                                  |
                                  v
                           Write to Archive
```

## Workflow Components

### 1. Scheduled Execution

The workflow starts with an n8n Schedule Trigger.

It is configured to execute automatically at a predefined time, using the `Asia/Tehran` timezone.

### 2. Journal File Management

Journal entries are stored as individual `.txt` files.

Each filename follows a date-based naming convention:

```text
YYYY-MM-DD.txt
```

Example:

```text
2026-10-28.txt
2026-10-29.txt
2026-10-30.txt
```

The project uses two directories:

```text
journals/
├── incoming/
│   ├── 2026-10-28.txt
│   ├── 2026-10-29.txt
│   └── 2026-10-30.txt
│
└── processed/
```

- `incoming`: Contains original journal entries waiting to be analyzed.
- `processed`: Contains generated archive files after successful processing.

The workflow reads the available files and selects only the newest entry based on its filename.

A Code node performs this selection by sorting the date-based filenames.

This prevents the workflow from analyzing every historical journal entry during each execution.

### 3. File Reading and Text Extraction

The Read/Write Files from Disk node reads journal files from the local filesystem.

The Binary to JSON node extracts the contents of each text file and converts them into JSON data.

An Edit Fields node preserves the original filename and other required metadata.

A Merge node combines the extracted journal text with its corresponding filename.

This ensures that the original file information remains available throughout the workflow.

### 4. Duplicate Processing Prevention

Before starting AI analysis, the workflow checks PostgreSQL to determine whether the selected journal file has already been processed.

Each journal filename is stored as a unique source identifier.

A PostgreSQL query checks whether a matching filename exists:

```sql
SELECT
    $1::text AS source_file,
    EXISTS (
        SELECT 1
        FROM journal_entries
        WHERE source_file = $1
    ) AS already_processed;
```

An IF node evaluates the result:

- If `already_processed` is `true`, the workflow skips the journal.
- If `already_processed` is `false`, the journal continues to the AI processing stages.

A unique index on the `source_file` column provides an additional database-level safeguard against duplicate records.

### 5. AI Sentiment and Emotion Analysis

The journal text is passed to an LLM using an n8n LLM Chain.

The model analyzes the journal and returns structured JSON containing:

- Sentiment classification.
- Detected emotions.
- Emotional intensity.
- An explanation of the emotional analysis.

Example output:

```json
{
  "sentiment": "positive",
  "emotions": [
    "happy",
    "excited"
  ],
  "intensity": 7,
  "explanation": "The entry reflects positive emotions, motivation, and social satisfaction."
}
```

A Code node parses the model's JSON response so that the extracted values can be used independently by subsequent nodes.

### 6. AI-Powered Personal Reflection

A second LLM Chain generates a personalized reflection using the original journal entry and its sentiment analysis.

Unlike the sentiment analysis stage, which focuses on structured data extraction, this stage focuses on contextual understanding and reflection.

The AI is instructed to provide a thoughtful, conversational response, addressing the journal writer directly rather than describing them in the third person.

The purpose is to provide meaningful feedback about the day's experiences, emotions, and behavioral patterns.

### 7. Telegram Notification

The generated reflection is sent to the user through a Telegram notification node.

This provides an immediate way to receive and read the AI-generated reflection without opening the n8n interface.

The Telegram integration is designed as a one-way notification system.

### 8. PostgreSQL Data Storage

The structured sentiment analysis is stored in PostgreSQL.

The database provides persistent storage for journal analysis results, allowing future querying and analysis.

The primary table is:

`journal_entries`

Its schema:

| Column | Data Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| journal_text | TEXT | Original journal entry |
| sentiment | VARCHAR(50) | Sentiment classification |
| emotions | TEXT[] | Extracted emotions |
| intensity | INTEGER | Emotional intensity |
| explanation | TEXT | AI-generated sentiment explanation |
| created_at | TIMESTAMP | Record creation timestamp |
| source_file | TEXT | Original journal filename |

The `source_file` column is protected by a unique index to prevent duplicate processing.

The `created_at` column uses a database default timestamp.

### 9. Preparing the Complete Archive

After the AI analysis, the Telegram notification, and the database insertion, the workflow prepares a complete archive.

The archive combines:

- Original journal filename.
- Original journal text.
- Sentiment classification.
- Extracted emotions.
- Emotional intensity.
- AI-generated sentiment explanation.
- AI-generated personal reflection.

An Edit Fields node prepares the required fields.

Another formatting step combines the information into a readable text document.

Example archive structure:

```text
JOURNAL ENTRY
========================================

Filename: 2026-10-30.txt

ORIGINAL JOURNAL
----------------------------------------
[Original journal content]

SENTIMENT ANALYSIS
----------------------------------------
Sentiment: positive
Emotions: ["happy", "excited"]
Intensity: 7/10

Explanation:
[AI-generated explanation]

AI REFLECTION
----------------------------------------
[AI-generated personal reflection]

========================================
```

The Convert to File node converts this formatted content into a text file.

Finally, the Read/Write Files from Disk node writes the generated archive into the `processed` directory.

The original journal file remains untouched in `incoming`.

This creates a separate, enriched record of each successfully processed journal entry.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| n8n | Workflow automation and orchestration |
| PostgreSQL | Structured data storage |
| Ollama | Local LLM execution |
| Mistral | Language model used for AI processing |
| Docker | Containerized n8n deployment |
| Telegram Bot API | Reflection notifications |
| JavaScript | Data transformation and workflow logic |

## Local Setup

### Prerequisites

Before running the project, make sure you have:

- Docker Desktop
- PostgreSQL
- pgAdmin 4 (optional, for database management)
- Ollama
- A downloaded Mistral model
- An n8n instance
- A Telegram bot and its credentials

### 1. Prepare the Journal Directories

Create the following directory structure:

```text
journals/
├── incoming/
└── processed/
```

Place your daily journal files inside `incoming`.

### 2. Run n8n with Docker

The following command runs n8n locally with persistent storage and access to the journal directories.

```powershell
docker run -it --rm --name n8n `
-p 5678:5678 `
-e TZ=Asia/Tehran `
-e GENERIC_TIMEZONE=Asia/Tehran `
-e N8N_HOST=localhost `
-e N8N_PORT=5678 `
-e N8N_RESTRICT_FILE_ACCESS_TO=/files `
-v "C:\Users\YOUR_USERNAME\Downloads:/files" `
-v n8n_data:/home/node/.n8n `
n8nio/n8n
```

Replace `YOUR_USERNAME` with your Windows username.

The Docker volume `n8n_data` preserves n8n configuration and workflow data between container restarts.

The Windows Downloads directory is mounted inside the container at `/files`.

### 3. Configure PostgreSQL

Create a database:

```sql
CREATE DATABASE journal_tracker;
```

Create the journal analysis table:

```sql
CREATE TABLE journal_entries (
    id SERIAL PRIMARY KEY,
    journal_text TEXT NOT NULL,
    sentiment VARCHAR(50) NOT NULL,
    emotions TEXT[],
    intensity INTEGER,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT
);
```

Create a unique index:

```sql
CREATE UNIQUE INDEX unique_journal_source_file
ON journal_entries (source_file)
WHERE source_file IS NOT NULL;
```

When connecting n8n to PostgreSQL running on the Windows host, use:

```text
Host: host.docker.internal
Port: 5432
Database: journal_tracker
```

Configure the remaining credentials according to your PostgreSQL installation.

### 4. Configure Ollama

Install Ollama and download the model:

```bash
ollama pull mistral
```

Make sure the model is available before executing the AI workflow.

Configure the appropriate Ollama credentials and model connections inside n8n.

### 5. Configure Telegram

Create a Telegram bot and configure its credentials in n8n.

Connect the Telegram node to the AI Reflection output so that the generated reflection can be delivered automatically.

### 6. Import the Workflow

Export the n8n workflow as a JSON file and import it into your n8n instance.

After importing, configure the required credentials:

- PostgreSQL
- Ollama
- Telegram

Verify the local file paths and schedule settings before activating the workflow.

**Important:** Credentials and API tokens should be configured inside n8n and must never be committed to the public repository.

---

## Project Design Decisions

Several design decisions were made during development:

**Date-based file naming**

Using `YYYY-MM-DD.txt` makes chronological sorting straightforward and allows the workflow to identify the newest journal entry without relying on filesystem modification timestamps.

**Database-based duplicate prevention**

PostgreSQL is the source of truth for processing status. The workflow checks the unique source filename before initiating AI analysis.

**Separate AI processing stages**

Sentiment extraction and personal reflection are handled by separate LLM Chains because they have different responsibilities and output requirements.

**Structured database storage**

Analytical fields are stored independently rather than saving the entire AI response as an unstructured text blob. This makes future querying and analysis easier.

**Local-first execution**

Using Docker and Ollama allows the automation and language model processing to run locally, reducing reliance on external AI APIs.

**Separate archival output**

The original journal remains unchanged, while the processed directory contains an enriched version combining the original entry with the AI-generated analysis.

---

## Future Improvements

Potential improvements include:

- Adding retry handling and error notifications.
- Improving duplicate-processing guarantees through transactional database operations.
- Supporting additional journal formats.
- Building a dashboard for tracking emotional trends over time.
- Generating weekly and monthly summaries.
- Adding analytical SQL queries to identify recurring emotional patterns.
- Improving the reflection prompt using historical journal context.
- Adding automated tests for data transformation and workflow behavior.

---

## Project Status

**Core workflow implemented.**

The system supports scheduled journal ingestion, newest-file selection, duplicate checking, AI-based sentiment and emotion analysis, personalized reflection generation, Telegram notifications, PostgreSQL persistence, and local text-file archiving.

The project is designed as a modular automation pipeline that can be extended with additional analytical and reporting capabilities.