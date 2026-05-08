# Privacy Doc Cleaner

A beginner-friendly Python web application that removes hidden identifying
metadata from PDF files — stripping author names, software signatures,
timestamps, and other personal identifiers invisibly embedded in your documents.

---

## Table of Contents

1. [What Problem Does This Solve](#1-what-problem-does-this-solve)
2. [Design Philosophy](#2-design-philosophy)
3. [Architecture](#3-architecture)
4. [Project Structure](#4-project-structure)
5. [How the App Flows](#5-how-the-app-flows)
6. [API Routes Reference](#6-api-routes-reference)
7. [Methods Reference](#7-methods-reference)
8. [Libraries Used](#8-libraries-used)
9. [Metadata Fields Removed](#9-metadata-fields-removed)
10. [Quick Start](#10-quick-start)
11. [Testing](#11-testing)
12. [Security Design](#12-security-design)
13. [Extending the Project](#13-extending-the-project)

---

## 1. What Problem Does This Solve

When you save a Word document as a PDF, Microsoft Office (and other software)
secretly embeds personal information inside the file. This information is
invisible when you read the PDF but can be extracted by anyone using free tools.

**Example of what gets embedded without your knowledge:**

| Hidden Field    | Example Value                  | Privacy Risk                      |
|-----------------|--------------------------------|-----------------------------------|
| `/Author`       | Jane Smith                     | Reveals your real name            |
| `/Creator`      | Microsoft Word 16.0            | Reveals your software version     |
| `/Producer`     | macOS Quartz PDFContext        | Reveals your operating system     |
| `/CreationDate` | D:20240315102345+05'30'        | Reveals exact creation time + timezone |
| `/ModDate`      | D:20240318090000+05'30'        | Reveals when you last edited it   |
| `/Company`      | Acme Corp Ltd                  | Reveals your organisation         |
| `/Manager`      | John Manager                   | Reveals your manager's name       |

This app strips all of these fields out, leaving only the visible content of
your document intact.

---

## 2. Design Philosophy

The application is designed around three core principles:

### Separation of Concerns
Each file has exactly one job. The web layer (`app.py`) never touches PDF
internals. The cleaning engine (`cleaner.py`) never knows about HTTP requests.
This makes the code easier to read, test, and extend.

### Privacy by Default
- Uploaded files are deleted immediately after processing
- No database stores your file history
- No user accounts or tracking
- The server holds your file for only the seconds it takes to clean it

### Beginner Readability
Every line of code is commented in plain English. The project is intentionally
kept small — two Python files, two HTML templates — so a beginner can read the
entire codebase in one sitting.

---

## 3. Architecture

The application has three distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│                        LAYER 1                              │
│                       Browser                               │
│         What the user sees and interacts with               │
│              index.html  |  result.html                     │
└──────────────────────┬──────────────────────────────────────┘
                       │  HTTP requests (GET / POST)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                        LAYER 2                              │
│                  Flask Web Layer                            │
│                      app.py                                 │
│                                                             │
│   Route /          →  serves the upload page               │
│   Route /upload    →  receives PDF, validates, delegates    │
│   Route /download  →  serves the cleaned file              │
└──────────────────────┬──────────────────────────────────────┘
                       │  Python function calls
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                        LAYER 3                              │
│               PDF Processing Engine                         │
│                     cleaner.py                              │
│                                                             │
│   read_pdf_metadata()    →  reads hidden metadata          │
│   clean_pdf_metadata()   →  strips metadata, saves copy    │
└──────────────────────┬──────────────────────────────────────┘
                       │  file read / write
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                        STORAGE                              │
│                                                             │
│   uploads/    →  temporary home for incoming PDFs          │
│   cleaned/    →  final home for processed PDFs             │
└─────────────────────────────────────────────────────────────┘
```

### Why Three Layers?

| Layer | Responsibility | Technology |
|-------|---------------|------------|
| Browser | Display UI, collect user input | HTML, CSS, JavaScript |
| Flask | Handle HTTP, validate input, coordinate | Python, Flask |
| Engine | PDF reading, writing, metadata stripping | Python, pypdf |

Each layer only talks to the layer directly next to it. The browser never
touches files directly. The engine never knows what URL was called.

---

## 4. Project Structure

```
privacy_doc_cleaner/
│
├── app.py                  ← Web layer: routes, validation, coordination
├── cleaner.py              ← Engine layer: PDF metadata stripping
├── requirements.txt        ← Python package dependencies
├── README.md               ← This file
│
├── templates/              ← HTML pages (Jinja2 templates)
│   ├── index.html          ← Upload page with drag-and-drop zone
│   └── result.html         ← Results page with before/after comparison
│
├── static/                 ← Static assets served directly to browser
│   ├── css/                ← Stylesheets (currently inline in HTML)
│   └── js/                 ← JavaScript files (currently inline in HTML)
│
├── uploads/                ← Temporary storage (auto-created at runtime)
│   └── .gitkeep            ← Keeps folder tracked by Git when empty
│
└── cleaned/                ← Processed PDFs awaiting download (auto-created)
    └── .gitkeep
```

---

## 5. How the App Flows

Below is the complete journey of a PDF from upload to download.

```
Step 1  User opens browser → visits localhost:5000
        Browser sends:  GET /
        Flask runs:     index()
        Flask returns:  index.html (the upload page)

Step 2  User picks a PDF → clicks "Clean Metadata"
        Browser sends:  POST /upload  (with PDF attached)
        Flask runs:     upload_file()

Step 3  Flask validates the upload
        ✓ Is a file attached?
        ✓ Is the filename non-empty?
        ✓ Is the extension .pdf?
        ✓ Is the filename safe? (secure_filename)
        ✗ Any failure → redirect back to index with error message

Step 4  Flask saves the file temporarily
        File saved to:  uploads/your_file.pdf

Step 5  Flask calls cleaner.py
        clean_pdf_metadata(upload_path, cleaned_path)

Step 6  cleaner.py reads the original metadata
        PdfReader opens the file
        reader.metadata → captures /Author, /Creator, etc.
        This is saved as "original_metadata" for the results page

Step 7  cleaner.py copies pages into a new PDF
        PdfWriter() creates a blank new PDF
        for page in reader.pages → writer.add_page(page)
        All visible content is copied. No metadata yet.

Step 8  cleaner.py wipes the metadata
        writer.add_metadata({})   ← empty dict = no metadata
        writer.write(output_file) ← saves the clean PDF to cleaned/

Step 9  Flask deletes the original upload
        os.remove(upload_path)
        The original file is gone. Only the clean copy remains.

Step 10 Flask renders the results page
        render_template("result.html",
            original_meta  = { metadata before cleaning },
            cleaned_meta   = { metadata after cleaning  },
            removed_fields = [ list of removed keys     ]
        )

Step 11 User clicks Download
        Browser sends:  GET /download/cleaned_your_file.pdf
        Flask runs:     download_file()
        Flask sends:    the clean PDF as a file download
```

---

## 6. API Routes Reference

The application exposes three HTTP routes. In Flask, a route is a URL that
triggers a Python function when visited.

---

### `GET /`

**Purpose:** Serve the homepage with the file upload form.

**Triggered by:** User visiting `http://localhost:5000` in a browser.

**Function:** `index()`

**Returns:** Renders `templates/index.html`

**Example:**
```
Request:   GET http://localhost:5000/
Response:  200 OK  +  index.html page
```

---

### `POST /upload`

**Purpose:** Receive an uploaded PDF, validate it, clean its metadata, and
return the results page.

**Triggered by:** User submitting the upload form.

**Function:** `upload_file()`

**Accepts:** `multipart/form-data` with a field named `file`

**Validation rules:**
- File field must be present in the request
- Filename must not be empty
- File extension must be `.pdf`
- File size must not exceed 16 MB (`MAX_CONTENT_LENGTH`)

**On success:** Renders `templates/result.html` with metadata comparison data

**On failure:** Redirects to `/` with a flash error message

**Example:**
```
Request:   POST http://localhost:5000/upload
           Content-Type: multipart/form-data
           Body: file=report.pdf

Response (success):  200 OK  +  result.html page
Response (failure):  302 Redirect → /  +  flash error message
```

**Data passed to result.html:**

| Variable | Type | Description |
|----------|------|-------------|
| `filename` | string | Name of the cleaned file, e.g. `cleaned_report.pdf` |
| `original_meta` | dict | Metadata key-value pairs before cleaning |
| `cleaned_meta` | dict | Metadata key-value pairs after cleaning |
| `removed_fields` | list | List of field names that were removed |

---

### `GET /download/<filename>`

**Purpose:** Serve a cleaned PDF file as a browser download.

**Triggered by:** User clicking the Download button on the results page.

**Function:** `download_file(filename)`

**URL parameter:** `filename` — the name of the cleaned file to download.
This is a dynamic segment: whatever comes after `/download/` in the URL
is passed into the function as the `filename` argument.

**Returns:** The PDF file as an attachment (triggers browser download dialog)

**On file not found:** Redirects to `/` with a flash error message

**Example:**
```
Request:   GET http://localhost:5000/download/cleaned_report.pdf
Response:  200 OK  +  file download (cleaned_report.pdf)
```

---

### `GET /api/metadata/<filename>` *(bonus endpoint)*

**Purpose:** Return a cleaned file's metadata as JSON. Useful for building
JavaScript-driven interfaces or automated testing.

**Function:** `get_metadata(filename)`

**Returns:** JSON object with metadata key-value pairs

**Example:**
```
Request:   GET http://localhost:5000/api/metadata/cleaned_report.pdf
Response:  200 OK
           {
             "/Title": "Quarterly Report",
             "/Pages": "12"
           }
```

---

## 7. Methods Reference

### Methods in `app.py`

---

#### `allowed_file(filename)`

Checks whether a filename has an allowed file extension.

```python
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | The uploaded filename, e.g. `report.pdf` |

**Returns:** `True` if the extension is in `ALLOWED_EXTENSIONS`, `False` otherwise.

**How it works:**
1. Checks that there is at least one dot in the filename
2. Splits on the last dot: `"report.pdf"` → `["report", "pdf"]`
3. Takes the part after the dot and checks if it is in `{"pdf"}`

**Examples:**
```python
allowed_file("report.pdf")   → True
allowed_file("photo.jpg")    → False
allowed_file("noextension")  → False
```

---

#### `index()`

Renders and returns the homepage.

```python
@app.route("/")
def index():
    return render_template("index.html")
```

**Returns:** The rendered `index.html` template as an HTTP response.

---

#### `upload_file()`

Handles the file upload form submission. Validates the upload, saves it
temporarily, calls the cleaner, deletes the original, and renders results.

```python
@app.route("/upload", methods=["POST"])
def upload_file():
    ...
```

**HTTP method:** POST only

**Steps performed:**
1. Check file field exists in `request.files`
2. Check filename is not empty
3. Check file extension with `allowed_file()`
4. Sanitise filename with `secure_filename()`
5. Save to `uploads/` folder
6. Call `clean_pdf_metadata()` from `cleaner.py`
7. Delete original from `uploads/`
8. Render `result.html` with before/after metadata

**Returns:** Rendered `result.html` on success, redirect to `/` on failure.

---

#### `download_file(filename)`

Serves a cleaned PDF file as a browser file download.

```python
@app.route("/download/<filename>")
def download_file(filename):
    ...
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Name of the file to download from `cleaned/` folder |

**Returns:** The file as an attachment using `send_file()`.

---

### Methods in `cleaner.py`

---

#### `read_pdf_metadata(pdf_path)`

Opens a PDF and reads all its metadata fields into a Python dictionary.

```python
def read_pdf_metadata(pdf_path):
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    if metadata is None:
        return {}
    return {key: str(value) for key, value in metadata.items()}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdf_path` | string | Full file path to the PDF to read |

**Returns:** Dictionary of metadata key-value pairs, or empty dict `{}` if
no metadata found, or `{"error": "message"}` if an exception occurs.

**Example return value:**
```python
{
    "/Author":       "Jane Smith",
    "/Creator":      "Microsoft Word 16.0",
    "/Producer":     "macOS Quartz PDFContext",
    "/CreationDate": "D:20240315102345+05'30'",
    "/ModDate":      "D:20240318090000+05'30'"
}
```

---

#### `clean_pdf_metadata(input_path, output_path)`

The main cleaning function. Reads a PDF, copies all pages into a new PDF
with no metadata, saves it, and returns a result summary.

```python
def clean_pdf_metadata(input_path, output_path):
    ...
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_path` | string | Full path to the original uploaded PDF |
| `output_path` | string | Full path where the cleaned PDF should be saved |

**Returns:** A dictionary with the following structure:

```python
# On success:
{
    "success":  True,
    "original": { "/Author": "Jane", ... },   # metadata before
    "cleaned":  {},                            # metadata after (empty)
    "removed":  ["/Author", "/Creator", ...]  # list of stripped fields
}

# On failure:
{
    "success": False,
    "error":   "Description of what went wrong"
}
```

**Internal steps:**
1. `PdfReader(input_path)` — opens the original PDF
2. `read_pdf_metadata(input_path)` — captures the "before" snapshot
3. `PdfWriter()` — creates a blank new PDF
4. `for page in reader.pages: writer.add_page(page)` — copies all pages
5. `writer.add_metadata({})` — sets metadata to empty
6. `writer.write(output_file)` — saves the clean PDF to disk
7. `read_pdf_metadata(output_path)` — captures the "after" snapshot
8. Computes which fields were removed by comparing before vs after

---

## 8. Libraries Used

### Flask `>=3.0`

The web framework that turns Python code into a web application.

| Flask Tool | Used For |
|------------|----------|
| `Flask` | Creates the application instance |
| `render_template` | Loads HTML files and injects data into them |
| `request` | Reads data sent from the browser (files, form fields) |
| `redirect` | Sends the user to a different URL |
| `url_for` | Generates URLs safely by route function name |
| `flash` | Sends one-time notification messages to the next page |
| `send_file` | Sends a file from the server to the browser |
| `jsonify` | Converts Python dicts to JSON for API responses |

Install: `pip install flask`
Docs: https://flask.palletsprojects.com

---

### pypdf `>=4.0`

A pure-Python library for reading and writing PDF files.

| pypdf Tool | Used For |
|------------|----------|
| `PdfReader` | Opens a PDF and reads its content and metadata |
| `PdfWriter` | Creates a new blank PDF |
| `reader.pages` | List of all pages in the PDF |
| `reader.metadata` | Dictionary of all metadata fields |
| `writer.add_page()` | Copies a page into the new PDF |
| `writer.add_metadata()` | Sets metadata — passing `{}` clears all fields |
| `writer.write()` | Saves the new PDF to disk |

Install: `pip install pypdf`
Docs: https://pypdf.readthedocs.io

---

### Werkzeug `>=3.0`

A utility library used internally by Flask. One tool is used directly.

| Werkzeug Tool | Used For |
|---------------|----------|
| `secure_filename` | Sanitises uploaded filenames to prevent path traversal attacks |

Install: Installed automatically with Flask.
Docs: https://werkzeug.palletsprojects.com

---

### Python Standard Library

These are built into Python — no installation needed.

| Module | Used For |
|--------|----------|
| `os` | Building file paths, creating directories, deleting files |
| `os.path.join` | Builds cross-platform file paths safely |
| `os.makedirs` | Creates the uploads/ and cleaned/ folders if they don't exist |
| `os.remove` | Deletes the original uploaded file after cleaning |
| `os.path.exists` | Checks whether a file exists before trying to serve it |

---

### Jinja2 (bundled with Flask)

The templating engine that lets you put Python data into HTML files.

| Jinja2 Syntax | Used For |
|---------------|----------|
| `{{ variable }}` | Outputs a Python variable's value into the HTML |
| `{% if condition %}` | Conditional blocks in HTML |
| `{% for item in list %}` | Loops through a Python list in HTML |
| `{{ list \| length }}` | Filters — `length` returns the count of a list |
| `get_flashed_messages()` | Retrieves flash messages sent by Flask |
| `url_for('route_name')` | Generates URLs safely inside HTML |

---

## 9. Metadata Fields Removed

The following standard PDF metadata fields are targeted for removal.
In practice, `add_metadata({})` clears all fields — this list documents
the ones most commonly found to contain identifying information.

| Field | Standard | Common Source | What It Reveals |
|-------|----------|---------------|-----------------|
| `/Author` | PDF spec | OS account name | Document creator's name |
| `/Creator` | PDF spec | Authoring software | e.g. Microsoft Word 16.0 |
| `/Producer` | PDF spec | PDF conversion tool | e.g. macOS Quartz, Acrobat |
| `/CreationDate` | PDF spec | System clock | Date, time, and timezone of creation |
| `/ModDate` | PDF spec | System clock | Date and time of last edit |
| `/Title` | PDF spec | Document title field | May contain project/client names |
| `/Subject` | PDF spec | Subject field | May contain sensitive context |
| `/Keywords` | PDF spec | Keywords field | May contain internal codes |
| `/Company` | Microsoft | Office account | Organisation name |
| `/Manager` | Microsoft | Office account | Manager's name |

---

## 10. Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (comes with Python)

### Installation

```bash
# 1. Navigate into the project folder
cd privacy_doc_cleaner

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

### Usage

1. Open your browser and go to `http://localhost:5000`
2. Upload any PDF file (max 16 MB)
3. Review the before/after metadata comparison
4. Download your cleaned PDF

### Stopping the app

Press `Ctrl+C` in the terminal.

---

## 11. Testing

### Manual Test Checklist

Run through these scenarios to verify the app is working correctly:

| Test | Action | Expected Result |
|------|--------|-----------------|
| Normal upload | Upload a PDF with metadata | Results page shows removed fields |
| No file selected | Click upload without choosing a file | Error: "Please select a file" |
| Wrong file type | Upload a `.jpg` or `.docx` | Error: "Only PDF files supported" |
| Download works | Click Download on results page | Clean PDF saved to your computer |
| Metadata gone | Check Properties of downloaded PDF | Author, Creator fields blank |
| Original deleted | Check uploads/ folder after cleaning | Folder is empty |

### Automated Tests

Create `test_cleaner.py` in the project root and run `python test_cleaner.py`:

```python
from cleaner import read_pdf_metadata, clean_pdf_metadata

def test_missing_file_returns_error():
    result = read_pdf_metadata("nonexistent.pdf")
    assert "error" in result
    print("PASS — missing file returns error dict")

def test_clean_missing_file_returns_failure():
    result = clean_pdf_metadata("ghost.pdf", "output.pdf")
    assert result["success"] == False
    print("PASS — clean of missing file returns success=False")

test_missing_file_returns_error()
test_clean_missing_file_returns_failure()
```

---

## 12. Security Design

| Measure | Implementation | Why |
|---------|---------------|-----|
| Filename sanitisation | `secure_filename()` | Prevents path traversal: `../../etc/passwd` |
| Extension whitelist | `ALLOWED_EXTENSIONS = {"pdf"}` | Blocks non-PDF uploads |
| File size limit | `MAX_CONTENT_LENGTH = 16MB` | Prevents large file denial-of-service |
| Immediate deletion | `os.remove(upload_path)` | Original never persists on server |
| Secret key | `app.secret_key` | Required for secure flash message signing |

**For production deployment, additionally:**
- Set `secret_key` from an environment variable, never hardcoded
- Run behind a WSGI server (gunicorn, not Flask's dev server)
- Use HTTPS (TLS certificate via Let's Encrypt)
- Add rate limiting (e.g. Flask-Limiter)

---

## 13. Extending the Project

| Feature | Library to add | Difficulty |
|---------|---------------|------------|
| Support Word (.docx) files | `python-docx` | Beginner |
| Support image EXIF data | `Pillow` | Beginner |
| Batch upload multiple files | Flask + HTML multiple attribute | Beginner |
| File history log | `Flask-SQLAlchemy` + SQLite | Intermediate |
| Auto-delete cleaned files after 1 hour | `APScheduler` | Intermediate |
| User login and accounts | `Flask-Login` | Intermediate |
| Deploy to the internet | Render / Railway / Fly.io | Intermediate |
| REST API for programmatic access | Flask + JSON responses | Intermediate |
| Docker container | Dockerfile | Advanced |

---

## Dependencies

```
flask>=3.0
pypdf>=4.0
werkzeug>=3.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## License

MIT — free to use, modify, and distribute.
