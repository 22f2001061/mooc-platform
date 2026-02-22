#!/usr/bin/env bash

echo "========================================="
echo "🚀 MOOC Local Demo Setup Starting..."
echo "========================================="

PROJECT_NAME="mooc"
SUPERUSER_USERNAME="admin"
SUPERUSER_EMAIL="admin@example.com"
SUPERUSER_PASSWORD="Admin@123"

STAFF_USERNAME="manager"
STAFF_EMAIL="manager@example.com"
STAFF_PASSWORD="Manager@123"

# ----------------------------------------
# 1. Create .env if not exists
# ----------------------------------------

if [ ! -f .env ]; then
  echo "🔧 Creating .env file..."
  cat <<EOF > .env
SECRET_KEY=unsafe-demo-secret-key
DEBUG=True
ALLOWED_HOSTS=*
DATABASE_URL=sqlite:///db.sqlite3
EOF
else
  echo "✅ .env already exists"
fi

# ----------------------------------------
# 2. Build & Start Docker
# ----------------------------------------

echo "🐳 Building Docker containers..."
docker-compose down -v
docker-compose -f docker-compose.dev.yml up --build -d

echo "⏳ Waiting for DB to be ready..."
sleep 5

# ----------------------------------------
# 3. Apply Migrations
# ----------------------------------------

echo "📦 Applying migrations..."
docker-compose exec -T web python manage.py migrate

# ----------------------------------------
# 4. Create Superuser
# ----------------------------------------

echo "👤 Creating superuser..."
docker-compose exec -T web python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username="$SUPERUSER_USERNAME").exists():
    User.objects.create_superuser(
        username="$SUPERUSER_USERNAME",
        email="$SUPERUSER_EMAIL",
        password="$SUPERUSER_PASSWORD"
    )
    print("Superuser created.")
else:
    print("Superuser already exists.")
EOF

# ----------------------------------------
# 5. Create Staff Manager User
# ----------------------------------------

echo "👨‍💼 Creating staff manager user..."
docker-compose exec -T web python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username="$STAFF_USERNAME").exists():
    user = User.objects.create_user(
        username="$STAFF_USERNAME",
        email="$STAFF_EMAIL",
        password="$STAFF_PASSWORD"
    )
    user.is_staff = True
    user.save()
    print("Manager user created.")
else:
    print("Manager already exists.")
EOF

# ----------------------------------------
# 6. Load Sample Data
# ----------------------------------------

echo "📚 Loading sample data..."
docker-compose exec -T web python manage.py loaddata fixtures/sample_data.json || true

# ----------------------------------------
# Done
# ----------------------------------------

echo ""
echo "========================================="
echo "🎉 MOOC DEMO READY!"
echo "========================================="
echo ""
echo "🌐 App:        http://localhost:8000"
echo "🛠 Staff UI:   http://localhost:8000/manage/"
echo "⚙️ Admin:      http://localhost:8000/admin/"
echo ""
echo "🔐 Superuser Credentials:"
echo "   Username: $SUPERUSER_USERNAME"
echo "   Password: $SUPERUSER_PASSWORD"
echo ""
echo "👨‍💼 Staff Manager Credentials:"
echo "   Username: $STAFF_USERNAME"
echo "   Password: $STAFF_PASSWORD"
echo ""
echo "========================================="