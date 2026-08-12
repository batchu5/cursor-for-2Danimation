# Running the Project Locally

## Backend Setup

### 1. Create a Virtual Environment & Install Dependencies

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file inside the `backend/` directory.

At a minimum, add:

```env
OPENROUTER_API_KEY=your_openrouter_key
SESSION_SECRET_KEY=some_secret_key
```

You'll also need to configure:

* MongoDB credentials
* Cloudinary credentials

Refer to the following files for the required environment variable names:

* `configurations.py`
* `cloudinary.py`

### 3. Start the Backend Server

```powershell
uvicorn main:app --reload
```

The FastAPI server will start at:

```
http://localhost:8000
```

---

## Frontend Setup

### 1. Install Dependencies

```powershell
cd frontend
npm install
```

### 2. Start the Development Server

```powershell
npm run dev
```

The frontend will start on:

```
http://localhost:5173
```

The frontend is already configured to communicate with the FastAPI backend running on `http://localhost:8000`.
