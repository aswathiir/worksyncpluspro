# Employee Tracker - Supabase Integration Setup

This guide will help you set up the Employee Tracker application with your Supabase database connection.

## Prerequisites

- Python 3.8+
- Node.js 14+
- Redis server (local or cloud)
- Supabase account and project

## Step 1: Supabase Configuration

1. **Get your Supabase credentials:**
   - Go to your Supabase project dashboard
   - Navigate to Settings > API
   - Copy the following values:
     - Project URL
     - Anon/Public key
     - Service Role key (for admin operations)

2. **Get your database connection string:**
   - Go to Settings > Database
   - Copy the connection string in this format:
     ```
     postgres://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
     ```

## Step 2: Environment Configuration

1. **Update the `.env` file** in the `ETWeb` directory with your actual Supabase credentials:

```env
# Django Configuration
SECRET_KEY=your-django-secret-key-here
DEBUG=True
USE_HTTPS=False
SIGNED_COOKIE_SALT=your-signed-cookie-salt-here

# Supabase Database Configuration
DATABASE_URL=postgres://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Email Configuration (optional)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Supabase Configuration
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

2. **Generate Django secret key:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

## Step 3: Installation

1. **Navigate to the web application directory:**
   ```bash
   cd ETWeb
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

## Step 4: Database Setup

1. **Run Django migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

## Step 5: Build Frontend

1. **Build the React frontend:**
   ```bash
   npm run build
   ```

2. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

## Step 6: Start Redis Server

1. **Install Redis** (if not already installed):
   - Windows: Download from https://redis.io/download
   - macOS: `brew install redis`
   - Ubuntu: `sudo apt-get install redis-server`

2. **Start Redis:**
   ```bash
   redis-server
   ```

## Step 7: Run the Application

1. **Start the Django development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Access the application:**
   - Web interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

## Step 8: Development Mode (Optional)

For development with hot reloading:

1. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

2. **In another terminal, start webpack in watch mode:**
   ```bash
   npm run dev
   ```

## Troubleshooting

### Database Connection Issues
- Verify your Supabase database URL is correct
- Check that your Supabase project is active
- Ensure your IP is whitelisted in Supabase (or disable IP restrictions)

### Redis Connection Issues
- Make sure Redis server is running
- Check the REDIS_URL in your .env file
- For cloud Redis, update the URL accordingly

### Frontend Build Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for Node.js version compatibility

### Migration Issues
- If you encounter migration conflicts, try:
  ```bash
  python manage.py migrate --fake-initial
  ```

## Features Available

Once running, you'll have access to:

- **Employee Management**: Track employee activities and productivity
- **Real-time Monitoring**: WebSocket-based live updates
- **Screenshot Collection**: Automated screenshot capture and storage
- **Project Management**: Create and manage projects with team members
- **Activity Analytics**: Visualize employee activity data
- **User Authentication**: Secure login/logout with token-based auth

## Next Steps

1. Configure the desktop client application (ETClient) to connect to your server
2. Set up email notifications (update EMAIL_* settings in .env)
3. Configure production settings for deployment
4. Set up SSL certificates for HTTPS in production

## Support

If you encounter issues:
1. Check the Django logs in the terminal
2. Verify all environment variables are set correctly
3. Ensure Supabase project is properly configured
4. Check Redis server status
