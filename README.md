# CodeQuest

CodeQuest is a Django coding practice platform for students. The current vertical slice is the coding challenge workflow: an admin manages challenges, a logged-in student browses challenges, submits an answer, receives an immediate result, and reviews only their own submissions.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and replace `[YOUR-PASSWORD]` with your Supabase database password. Percent-encode special characters in the password before placing it in `DATABASE_URL`.
4. Run `python manage.py migrate`.
5. Create an administrator with `python manage.py createsuperuser`. Public registration creates student accounts only.
6. Load the starter collection with `python manage.py seed_challenges`.
7. Start the server with `python manage.py runserver`.

The application uses PostgreSQL/Supabase by default. SQLite is available only when `USE_SQLITE_DEV=True` is explicitly set for offline development and tests.

## Core Feature Flow

- Admins create, edit, view, and delete coding challenges.
- Students browse challenge details and submit answers.
- Submissions are stored with student and challenge foreign keys.
- Answers are checked against the challenge's expected output.
- Students can view their own submission history; other users' submissions are not exposed.

## Account Feature

- Registration validates required fields, email format, uniqueness, and matching passwords.
- Django authentication hashes passwords and protects authenticated pages.
- Student and Admin users are routed to role-specific dashboards.
- Users can view and update only their own profile details.

## Testing

Run the full test suite with `python manage.py test`. For an offline environment, set `USE_SQLITE_DEV=True` in `.env` before running tests; the test database is created and removed by Django. The suite covers registration and role protection, challenge validation and submission, record privacy, HTTP methods, and custom error pages.
