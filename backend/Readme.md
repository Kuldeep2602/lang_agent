# Backend Setup => 

cd backend
python -m venv venv
venv\Scripts\activate  
# macOS/Linux:
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Create .env file (copy from example)
cp .env.example .env
# Run migrations
python manage.py migrate
# Start the server
python manage.py runserver