# MediConnect Backend

Production-ready healthcare platform backend built with Node.js, Express, MySQL, Socket.IO, and Zoom API.

## Features
- ✅ JWT Authentication & RBAC
- ✅ MySQL with transaction support
- ✅ Real-time chat (Socket.IO)
- ✅ Zoom video integration
- ✅ AWS S3 file storage
- ✅ PDF prescription generation
- ✅ Cron jobs for appointment unlocking
- ✅ Double-booking prevention
- ✅ Emergency & scheduled appointments

## Prerequisites
- Node.js 16+  
- MySQL 8.0+
- AWS Account (for S3)
- Zoom Account (for Video API)

## Installation

1. **Install dependencies:**
   ```bash
   cd backend
   npm install
   ```

2. **Configure environment variables:**
   Edit `.env` file with your credentials:
   ```env
   # Database
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=mediconnect_db

   # JWT
   JWT_SECRET=your_secret_key

   # AWS S3
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_S3_BUCKET=your_bucket
   AWS_REGION=us-east-1

   # Zoom API
   ZOOM_API_KEY=your_key
   ZOOM_API_SECRET=your_secret
   ZOOM_ACCOUNT_ID=your_account_id
   ```

3. **Initialize database:**
   ```bash
   npm run init-db
   ```

   This will:
   - Create database
   - Create all tables
   - Seed admin account

4. **Start server:**
   ```bash
   # Development
   npm run dev

   # Production
   npm start
   ```

## API Endpoints
### Authentication
- `POST /api/auth/register` - Register patient
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update profile

### Patients
- `GET /api/patients/doctors` - Browse doctors
- `GET /api/patients/doctors/:id` - Doctor details
- `GET /api/patients/time-slots` - Available time slots

### Appointments
- `POST /api/appointments/scheduled` - Book scheduled appointment
- `POST /api/appointments/emergency` - Book emergency appointment
- `GET /api/appointments/my` - Get my appointments
- `GET /api/appointments/:id` - Get appointment details

### Admin
- `POST /api/admin/doctors` - Create doctor
- `GET /api/admin/doctors` - Get all doctors
- `PATCH /api/admin/doctors/:id/approve` - Approve doctor
- `POST /api/admin/availability` - Set doctor availability
- `GET /api/admin/stats` - Dashboard statistics

### Chat
- `GET /api/chat/:appointment_id/messages` - Get messages
- `POST /api/chat/message` - Send message

### Prescriptions
- `POST /api/prescriptions` - Create prescription
- `GET /api/prescriptions/my` - Get my prescriptions

### Upload
- `POST /api/upload` - Upload file to S3

## Socket.IO Events

### Client → Server
- `join-chat` - Join appointment chat room
- `send-message` - Send message
- `typing` - Typing indicator
- `leave-chat` - Leave chat room

### Server → Client
- `joined-chat` - Successfully joined
- `message-history` - Recent messages
- `receive-message` - New message
- `prescription-shared` - Prescription shared
- `user-typing` - User is typing

## Database Schema

### Tables
1. **users** - Authentication & roles
2. **doctors** - Doctor profiles
3. **patient_profiles** - Patient information
4. **availability** - Doctor schedules
5. **appointments** - Bookings
6. **messages** - Chat history
7. **prescriptions** - Digital prescriptions
8. **payments** - Transaction records

## Admin Credentials (Development)

- Email: admin@mediconnect.com
- Password: Password@1

**⚠️ Change these in production!**

## License

MIT
