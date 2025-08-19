# Journal App Backend Integration Contracts

## Authentication System
### Environment Variables
- `ADMIN_PASSWORD` - hashed admin password (bcryptjs)
- `VIEWER_PASSWORD` - hashed viewer password (bcryptjs)

### Session Management
- HTTP-only cookies for session storage
- Role-based authentication (admin/viewer)
- Secure cookie flags for production

## API Endpoints

### Authentication
```
POST /api/login
Input: { password: string }
Output: { role: 'admin' | 'viewer', message: string }
Sets: HTTP-only cookie with role and session
```

```
POST /api/logout
Output: { message: string }
Clears: Session cookie
```

### Entries Management
```
GET /api/entries?search={query}&category={category}
Headers: Cookie (session)
Output: { entries: Entry[], grouped: GroupedEntries }
Rules: Admin sees all, Viewer sees only shared entries
```

```
POST /api/entries
Headers: Cookie (admin only)
Input: { title, content, category, tags: string[], isShared: boolean }
Output: { entry: Entry, message: string }
```

```
PUT /api/entries/{id}
Headers: Cookie (admin only)
Input: { title?, content?, category?, tags?: string[], isShared?: boolean }
Output: { entry: Entry, message: string }
```

```
DELETE /api/entries/{id}
Headers: Cookie (admin only)
Output: { message: string }
```

### Categories Management
```
GET /api/categories
Headers: Cookie (session)
Output: { categories: string[] }
```

```
POST /api/categories
Headers: Cookie (admin only)
Input: { name: string }
Output: { category: string, message: string }
```

## Database Models

### Entry Model
```python
{
  "id": "uuid",
  "title": "string",
  "content": "string", 
  "category": "string",
  "tags": ["string"],
  "isShared": "boolean",
  "dateCreated": "datetime",
  "dateModified": "datetime"
}
```

### Category Collection
- Derived from entries, no separate model needed
- Dynamic category list from existing entries

## Frontend Integration Changes

### Mock Data Replacement
Replace these mock functions in frontend:
- `getMockEntries()` → API call to `/api/entries`
- `addMockEntry()` → API call to `POST /api/entries`
- `updateMockEntry()` → API call to `PUT /api/entries/{id}`
- `deleteMockEntry()` → API call to `DELETE /api/entries/{id}`
- `searchMockEntries()` → API call to `/api/entries?search={query}`

### Authentication Integration
- Replace mock login in `NumericKeypad.jsx` with API call
- Add API error handling for invalid passwords
- Implement automatic logout on session expiry
- Add loading states for all API calls

### Session Management
- Remove localStorage role storage
- Rely on HTTP-only cookies for authentication
- Add session validation on route changes
- Handle authentication errors gracefully

## Security Features
- Bcrypt password hashing (saltRounds: 12)
- HTTP-only cookies prevent XSS
- Secure cookies in production
- Input validation on all endpoints
- Role-based middleware protection
- Rate limiting on login endpoint

## Error Handling
```python
{
  "error": "string",
  "message": "string", 
  "statusCode": "number"
}
```

### Error Codes
- 400: Invalid input data
- 401: Unauthorized (invalid password/session)
- 403: Forbidden (insufficient permissions)
- 404: Resource not found
- 429: Rate limit exceeded
- 500: Internal server error

## Implementation Priority
1. Setup bcrypt password hashing in .env
2. Create authentication middleware
3. Implement login/logout endpoints
4. Create entries CRUD operations
5. Add search and filtering
6. Integrate frontend with real APIs
7. Replace all mock data usage
8. Add comprehensive error handling