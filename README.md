# LeaveDesk

## About
LeaveDesk is a backend application built using Python and FastAPI. It helps employees apply for leave and Work From Home (WFH). Managers can view and manage employee requests.

## Technologies Used
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- bcrypt

---

## 1. Authentication

- Users can log in using email and password.
- JWT tokens are used for secure login.
- Passwords are stored in hashed format.
- Two roles are available: Employee and Manager.
- Only managers can access manager-specific features.
- Users can view their own profile.
- Invalid login details return an error.

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/login` | User login |
| GET | `/auth/me` | View user profile |

---

## 2. Leave Management

- Employees can apply for leave.
- Leave types: CASUAL, SICK, EARNED.
- Leave duration: FULL_DAY, HALF_DAY, HOURS.
- Employees can view their own leave requests.
- Employees can cancel pending requests.
- The system prevents overlapping leave requests.
- Leave requests start with PENDING status.

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leaves` | Apply for leave |
| GET | `/leaves/me` | View own leaves |
| POST | `/leaves/{id}/cancel` | Cancel leave |

---

## 3. Work From Home (WFH)

- Employees can apply for WFH.
- Employees can select start date and end date.
- Maximum two working days are allowed.
- Weekends are excluded from working-day calculation.
- Employees can view their own WFH requests.
- Employees can cancel pending requests.
- The system prevents overlapping WFH requests.
- WFH cannot overlap with active full-day leave requests.

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/wfh` | Apply for WFH |
| GET | `/wfh/me` | View own WFH requests |
| POST | `/wfh/{id}/cancel` | Cancel WFH |

---

## 4. Manager Management

- Managers can view requests from their direct employees.
- Managers can filter requests by status, employee ID, and date.
- Managers can approve or reject leave requests.
- Managers can approve or reject WFH requests.
- Managers can add comments while making decisions.
- Only pending requests can be approved or rejected.
- Employees cannot access manager endpoints.

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/manager/requests` | View employee requests |
| POST | `/manager/leaves/{id}/approve` | Approve leave |
| POST | `/manager/leaves/{id}/reject` | Reject leave |
| POST | `/manager/wfh/{id}/approve` | Approve WFH |
| POST | `/manager/wfh/{id}/reject` | Reject WFH |

---

## Project Status

Completed modules:
1. Authentication
2. Leave Management
3. Work From Home
4. Manager Management