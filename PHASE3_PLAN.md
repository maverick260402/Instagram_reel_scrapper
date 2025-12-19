# Phase 3: Admin Panel & Advanced Features

**Status**: Planning
**Start Date**: December 18, 2025

## 📋 Overview

Phase 3 adds a comprehensive admin panel with user management, Instagram account monitoring, activity logs, real-time notifications, and advanced analytics.

## 🎯 Goals

1. **Admin Panel UI** - Web-based dashboard for system administration
2. **User Management** - CRUD operations for users, credit limits, and permissions
3. **Instagram Account Management** - Monitor and manage the account pool
4. **Activity Logs Viewer** - Search, filter, and analyze system events
5. **System Statistics** - Real-time dashboard with charts and metrics
6. **Real-time Notifications** - Live updates for jobs, errors, and system events
7. **Advanced Analytics** - Deeper insights into scraping performance

## 🛠 Technology Stack

### Frontend
- **Framework**: Vanilla JavaScript (consistent with current frontend)
- **Alternative**: React.js (if user prefers SPA)
- **UI Library**: Tailwind CSS or Bootstrap 5
- **Charts**: Chart.js or ApexCharts
- **Icons**: Font Awesome or Heroicons

### Backend
- **Existing**: FastAPI (no changes needed)
- **WebSockets**: FastAPI WebSocket support for real-time updates
- **Alternative**: Server-Sent Events (SSE) for simpler implementation

### Database
- **No schema changes required** (all tables exist from Phase 1 & 2)
- **Views**: May add database views for complex queries

## 📐 Architecture

```
Frontend/
├── admin/
│   ├── index.html          # Admin dashboard main page
│   ├── admin.js            # Admin panel logic
│   ├── admin.css           # Admin panel styles
│   ├── components/
│   │   ├── users.js        # User management component
│   │   ├── accounts.js     # Instagram account management
│   │   ├── logs.js         # Activity logs viewer
│   │   ├── stats.js        # Statistics dashboard
│   │   └── notifications.js # Real-time notifications
│   └── utils/
│       ├── api.js          # API client
│       ├── charts.js       # Chart helpers
│       └── websocket.js    # WebSocket client

Backend/
├── app.py                  # Add admin endpoints and WebSocket
├── admin_routes.py         # NEW: Admin-specific routes
├── websocket_manager.py    # NEW: WebSocket connection manager
└── analytics.py            # NEW: Advanced analytics functions
```

## 📡 New API Endpoints

### User Management
```
GET    /api/admin/users                    # List all users
GET    /api/admin/users/{user_id}          # Get user details
PUT    /api/admin/users/{user_id}          # Update user
DELETE /api/admin/users/{user_id}          # Delete user (soft delete)
PUT    /api/admin/users/{user_id}/credits  # Update credit limit
PUT    /api/admin/users/{user_id}/status   # Activate/deactivate
GET    /api/admin/users/{user_id}/stats    # User usage statistics
```

### Instagram Account Management
```
GET    /api/admin/instagram-accounts        # Already exists
GET    /api/admin/instagram-accounts/{id}   # Get account details
PUT    /api/admin/instagram-accounts/{id}   # Update account
POST   /api/admin/instagram-accounts/test   # Test account cookies
GET    /api/admin/instagram-accounts/stats  # Pool statistics
```

### Activity Logs
```
GET    /api/admin/logs                      # List logs with filters
GET    /api/admin/logs/stats                # Log statistics
GET    /api/admin/logs/export               # Export logs as CSV
```

### System Statistics
```
GET    /api/admin/stats/overview            # System overview
GET    /api/admin/stats/usage               # Usage over time
GET    /api/admin/stats/performance         # Performance metrics
GET    /api/admin/stats/errors              # Error rates
```

### Real-time Updates
```
WS     /ws/admin                            # WebSocket for live updates
GET    /api/admin/events/stream             # SSE alternative
```

## 🎨 UI Components

### 1. Dashboard Overview
- **Total Users**: Active, inactive counts
- **Total Instagram Accounts**: Active, paused, cookie health
- **Today's Stats**: Reels scraped, jobs completed, credits used
- **Recent Activity**: Last 10 events
- **Charts**:
  - Daily scraping trends (last 7 days)
  - Credit usage by user
  - Account usage distribution
  - Success/failure rates

### 2. User Management
- **Table View**: Email, username, credits used/limit, status, actions
- **Filters**: Status (active/inactive), credit usage, last login
- **Sort**: By name, email, credits, last active
- **Actions**:
  - Edit credit limit
  - Reset password
  - View activity logs
  - Activate/deactivate
  - View user statistics
- **User Details Modal**:
  - Basic info (email, username, created date)
  - Credit usage chart
  - Recent scraping jobs
  - Activity timeline

### 3. Instagram Account Management
- **Table View**: Username, email, cookie health, daily count, total scrapes, status
- **Filters**: Status, cookie age, usage level
- **Sort**: By usage, success rate, last used
- **Actions**:
  - Update cookies
  - Pause/resume
  - Test cookies
  - View usage history
- **Account Details Modal**:
  - Cookie information (last updated, age)
  - Usage statistics (chart)
  - Success/failure rates
  - Recent jobs using this account

### 4. Activity Logs Viewer
- **Table View**: Timestamp, event type, user, Instagram account, details
- **Filters**:
  - Date range picker
  - Event type dropdown
  - User filter
  - Instagram account filter
  - Search in details
- **Export**: Download filtered logs as CSV
- **Live Updates**: Auto-refresh toggle

### 5. Statistics Dashboard
- **Time Period Selector**: Today, Last 7 days, Last 30 days, Custom range
- **Charts**:
  - Total reels scraped over time (line chart)
  - Credit consumption by user (bar chart)
  - Account usage distribution (pie chart)
  - Success vs failure rates (donut chart)
  - Peak usage hours (heatmap)
- **Metrics Cards**:
  - Total reels scraped
  - Average reels per job
  - Most active user
  - Most used Instagram account
  - System uptime

### 6. Real-time Notifications
- **Notification Bell**: Badge count for new events
- **Notification Panel**: Dropdown with recent events
- **Event Types**:
  - Job started
  - Job completed
  - Job failed
  - Credit limit reached
  - No accounts available
  - Cookie update success/failure
  - Daily reset completed
- **Toast Notifications**: Pop-up for important events

## 🔐 Security

### Admin Authentication
- **Admin User Table**: Already exists from Phase 1
- **Login Endpoint**: `/api/admin/auth/login`
- **Session Management**: JWT tokens with admin role
- **Middleware**: Verify admin role for all `/api/admin/*` endpoints

### Permissions
- **Admin Role**: Full access to all admin features
- **Read-only Mode**: View-only access for monitoring

## 📊 Database Queries

### Optimizations Needed
1. **Add indexes** for common filters:
   ```sql
   CREATE INDEX idx_activity_logs_event_type ON activity_logs(event_type);
   CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);
   CREATE INDEX idx_scraped_reels_scraped_at ON scraped_reels(scraped_at);
   ```

2. **Create views** for complex stats:
   ```sql
   CREATE VIEW v_daily_stats AS
   SELECT
     DATE(scraped_at) as date,
     COUNT(*) as total_reels,
     COUNT(DISTINCT user_id) as active_users,
     AVG(play_count) as avg_plays
   FROM scraped_reels
   GROUP BY DATE(scraped_at);
   ```

## 🚀 Implementation Plan

### Step 1: Backend Foundation (2-3 hours)
- [ ] Create `admin_routes.py` with all admin endpoints
- [ ] Add admin authentication middleware
- [ ] Implement user management CRUD operations
- [ ] Add statistics calculation functions
- [ ] Create database indexes and views

### Step 2: Frontend Structure (1-2 hours)
- [ ] Create admin panel HTML structure
- [ ] Set up routing for admin pages
- [ ] Create base CSS with sidebar navigation
- [ ] Implement authentication flow

### Step 3: User Management UI (2-3 hours)
- [ ] Build user list table with filters
- [ ] Create user edit modal
- [ ] Implement credit limit updates
- [ ] Add user statistics view

### Step 4: Instagram Account Management UI (2-3 hours)
- [ ] Build account list table with filters
- [ ] Create account details modal
- [ ] Implement cookie testing
- [ ] Add usage charts

### Step 5: Activity Logs Viewer (2-3 hours)
- [ ] Build logs table with advanced filters
- [ ] Implement date range picker
- [ ] Add search functionality
- [ ] Create CSV export feature

### Step 6: Statistics Dashboard (3-4 hours)
- [ ] Create dashboard layout
- [ ] Implement Chart.js charts
- [ ] Add metrics cards
- [ ] Create time period selector

### Step 7: Real-time Notifications (3-4 hours)
- [ ] Implement WebSocket server
- [ ] Create WebSocket client
- [ ] Build notification UI
- [ ] Add toast notifications

### Step 8: Testing & Polish (2-3 hours)
- [ ] Test all admin features
- [ ] Add loading states
- [ ] Implement error handling
- [ ] Create admin documentation

**Total Estimated Time**: 17-25 hours

## 📝 Configuration

### Environment Variables
```env
# Admin Panel
ADMIN_PANEL_ENABLED=true
ADMIN_SESSION_SECRET=your-secret-key-here
ADMIN_TOKEN_EXPIRY=86400  # 24 hours

# WebSocket
WEBSOCKET_ENABLED=true
WEBSOCKET_PING_INTERVAL=30
```

## 🧪 Testing Strategy

1. **Unit Tests**: Test all new endpoints
2. **Integration Tests**: Test admin workflows end-to-end
3. **Load Tests**: Test WebSocket with multiple connections
4. **Security Tests**: Verify admin authentication and authorization

## 📚 Documentation Updates

1. Add Phase 3 section to CLAUDE.md
2. Create admin panel user guide
3. Document all new API endpoints
4. Add troubleshooting for WebSocket issues

## 🎁 Bonus Features (Optional)

- **Email Notifications**: Send alerts via email
- **Backup/Export**: Export system data
- **System Health Checks**: Automated monitoring
- **Role-based Access Control**: Multiple admin levels
- **Audit Trail**: Track all admin actions
- **Dark Mode**: UI theme switcher

## 🏁 Success Criteria

- ✅ Admin can manage users (view, edit, activate/deactivate)
- ✅ Admin can monitor Instagram accounts (status, cookies, usage)
- ✅ Admin can view and filter activity logs
- ✅ Admin can see system statistics with charts
- ✅ Real-time notifications for important events
- ✅ All features work smoothly without lag
- ✅ Admin panel is secure and requires authentication
- ✅ UI is responsive and user-friendly
