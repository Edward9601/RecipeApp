# 🍲 RecipeApp
A Django-based recipe website where users can create, view, and manage their own recipes. Each recipe includes multiple ingredients and step-by-step instructions. Users can also add sub-recipes, upload images, and filter recipes by ingredient or title.

## 🌐 Live Demo

WebSite URL: https://recipeapp-17q5.onrender.com

## 🔧 Tech Stack
- Python 3
- Django 5.x
- PostgreSQL
- Redis (for caching and session storage)
- Render (deployment)
- Bootstrap5
- HTML/HTMX/CSS/JS/TypeScript (frontend)

## 📦 Features
- User registration and login (Django's built-in user model)
- Create, edit, and delete personal recipes
- Add multiple ingredients per recipe (with optional measurement)
- Add ordered steps to each recipe
- Sub-recipes: recipes within recipes, each with their own ingredients and steps
- Filter recipes by ingredient names and recipe title
- Responsive UI with Bootstrap5
- Image upload for recipes (optional)
- Caching with Redis for improved performance
- Comprehensive backend form validation and unit tests

## 🚀 Setup Instructions

1. **Clone the repository:**
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Install Node.js and npm (if not already installed):**
   - On macOS:
     ```bash
     brew install node
     ```
   - Or download from https://nodejs.org/
5. **Install TypeScript and frontend dependencies:**
   ```bash
   npm install -g typescript
   npm install
   ```
6. **Compile TypeScript:**
   ```bash
   tsc
   ```
   - Or use your project's build script if available (e.g., `npm run build`).
7. **Set up environment variables:**
   - Create a `.env` file in your project root or export variables in your shell for database, Redis, secret key, and (if using) AWS S3 storage.
   - Example `.env` file:
     ```env
     SECRET_KEY='your-secret-key'
     
     # local development block
     ENVIRONMENT='local'
     DB_ENGINE='django.db.backends.postgresql'
     DB_NAME='dev_db'
     DB_USER='your-db-user'
     DB_PASSWORD='your-db-password'
     DB_HOST='localhost'
     DB_PORT='5432'

     DATABASE_URL='postgresql://user:password@localhost:5432/yourdb'
     LOCAL_REDIS_URL='redis://127.0.0.1:6379' # local develpment
     REDIS_URL='redis://localhost:6379/1'
     # AWS S3 (optional, for media storage)
     AWS_ACCESS_KEY_ID='your-aws-access-key-id'
     AWS_SECRET_ACCESS_KEY='your-aws-secret-access-key'
     AWS_STORAGE_BUCKET_NAME='your-bucket-name'
     AWS_S3_REGION_NAME='your-aws-region'
     ```
8. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
9. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```
10. **Run the development server:**
    ```bash
    python manage.py runserver
    ```
11. **Deploying to Render & Neon:**
    - **Render:**
      1. Push your code to a GitHub repository.
      2. Create a new Web Service on Render and connect your repo.
      3. Set environment variables in the Render dashboard (copy from your `.env` file, but never commit secrets to git).
      4. Set the build and start commands:
         - Build command: `pip install -r requirements.txt && npm install && npm run build && python manage.py collectstatic --noinput`
         - Start command: `gunicorn mywebsite.wsgi`
      5. Add a Render disk for media files if needed, or configure AWS S3 for media storage.
      6. For static files, ensure you run `collectstatic` and configure your static/media settings for production.
    - **Neon (PostgreSQL):**
      1. Create a Neon project and database at https://neon.tech/.
      2. Copy the connection string (e.g., `postgresql://...`) and set it as your `DATABASE_URL` in Render's environment variables.
      3. Make sure your Django settings use `DATABASE_URL` for the database configuration.
      4. Apply migrations after deployment: `python manage.py migrate` (can be set as a Render deploy hook).

## 🧠 Future Plans
- Dockerization
- Full React frontend
- AWS Cognito
