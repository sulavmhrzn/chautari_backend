# [Authentication Workflow (Notion-style)](https://aryaniyaps.medium.com/better-email-verification-workflows-13500ce042c7)
> **⚠️ IMPLEMENTATION NOTE:** This advanced authentication workflow will not be implemented until beta/stable release. The current MVP will use traditional email + password signup for faster development and initial user testing. This document serves as a future enhancement roadmap.

## Overview
This workflow prioritizes email verification first, then password creation. Users can access the app with a temporary code before setting a permanent password.

## Data Model Requirements

### User Model Fields
- `email` (unique)
- `password` (nullable)
- `has_password` (boolean, default=False)
- `email_verified` (boolean, default=False)
- `first_name`, `last_name` (optional, can be set later)

### VerificationCode Model
- `user` (ForeignKey to User)
- `code` (6-digit string)
- `expires_at` (timestamp)
- `is_used` (boolean, default=False)

## Workflow Steps

### Step 1: Email Entry
**Frontend:** `/signup` page with only email field
**User Action:** Enters email and clicks "Continue"

```json
POST /api/auth/check-email/
{
  "email": "user@example.com"
}
```

### Step 2: Account Check
**Backend Logic:**
- Check if user exists with this email
- If user exists AND `has_password = true` → Return "user_exists_with_password"
- If user exists AND `has_password = false` → Return "user_exists_without_password" 
- If user doesn't exist → Return "user_not_found"

**Response Examples:**
```json
// Case 1: Existing user with password
{
  "success": true,
  "data": {
    "status": "user_exists_with_password",
    "message": "Account exists. Please login with your password."
  }
}

// Case 2: Existing user without password (previous incomplete signup)
{
  "success": true,
  "data": {
    "status": "user_exists_without_password",
    "message": "Verification code sent to your email."
  }
}

// Case 3: New user
{
  "success": true,
  "data": {
    "status": "user_not_found",
    "message": "Verification code sent to your email."
  }
}
```

### Step 3: User Creation & Code Generation
**For Cases 2 & 3:**
1. Create user (if doesn't exist) with:
   - `email_verified = false`
   - `has_password = false` 
   - `password = null`
2. Generate 6-digit verification code
3. Save code with 10-minute expiry
4. Send email with verification code

### Step 4: Code Verification
**Frontend:** Show code input field
**User Action:** Enters 6-digit code

```json
POST /api/auth/verify-email/
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Backend Logic:**
- Validate code (correct, not expired, not used)
- If valid:
  - Set `email_verified = true`
  - Mark code as `is_used = true`
  - Generate temporary JWT tokens
  - Return tokens

**Success Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token_here",
    "refresh_token": "refresh_token_here",
    "user": {
      "email": "user@example.com",
      "has_password": false,
      "email_verified": true
    }
  }
}
```

### Step 5: Dashboard Access
**Frontend:** User is logged in and redirected to dashboard
**User Experience:** 
- Can access the app with limited functionality
- Prominent banner/modal: "Set your password to secure your account"

### Step 6: Password Creation
**Frontend:** Password setup modal/page (triggered automatically or manually)
**User Action:** Sets permanent password

```json
POST /api/auth/set-password/
Authorization: Bearer <access_token>
{
  "password": "strong_password_123"
}
```

**Backend Logic:**
- Validate password strength
- Hash and save password
- Set `has_password = true`

### Step 7: Complete Account
**User now has:**
- ✅ Verified email
- ✅ Secure password  
- ✅ Full app access

## API Endpoints

```
POST /api/auth/check-email/          # Check if email exists
POST /api/auth/verify-email/         # Verify email with code
POST /api/auth/set-password/         # Set permanent password (authenticated)
POST /api/auth/login/                # Login with email + password
POST /api/auth/resend-code/          # Resend verification code
```

## Edge Cases

### Expired Code
- Generate new code
- Send new email
- Previous codes become invalid

### Multiple Signup Attempts
- Invalidate previous codes
- Generate fresh code each time

### User Changes Mind
- If user navigates away and comes back
- Check current state and resume from appropriate step

## Benefits

1. **Immediate Access:** Users can start using the app before setting a password
2. **Email Verification First:** Ensures email ownership before account creation
3. **Reduced Friction:** No password requirements during initial signup
4. **Security:** Email verification + eventual password requirement
5. **Recovery Friendly:** Users who forget passwords can easily restart the flow

## Frontend State Management

```javascript
// User states to track
const authStates = {
  EMAIL_ENTRY: 'email_entry',
  CODE_VERIFICATION: 'code_verification', 
  LOGIN_REQUIRED: 'login_required',
  PASSWORD_SETUP: 'password_setup',
  AUTHENTICATED: 'authenticated'
}
```


---

*This document serves as a specification for future implementation and should be revisited during the beta development phase.*