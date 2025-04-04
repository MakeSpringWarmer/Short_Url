# HTTP APIs for Short URL System with Redirection

A FastAPI-based URL shortening service with automatic redirection and input validation.


## API Documentation

### **1. Create Short URL**

#### Endpoint
`POST /shorten`

#### Request
```Json
{
"original_url": "https://long-url-needs-shorter/"
}
```


#### Response (Success)

```Json
{
   "short_url": "http://your_domain/abc12345",
   "expiration_date": "2025-12-31T16:21:00",
   "success": true,
   "reason": null
}
```

#### Response (Error)
```Json
{
"short_url": null,
"expiration_date": null,
"success": false,
"reason": "Error message"
}
```


**Possible Errors**:
- `400 Bad Request`: 
  - URL exceeds 2048 characters
  - Invalid URL format
  - URL not publicly accessible
- `500 Internal Server Error`: Database failure

---

### **2. Redirect to Original URL**

#### Endpoint
`GET /{short_id}`

#### Parameters
| Name      | Type   | Description       |
|-----------|--------|-------------------|
| `short_id`| string | 8-character ID    |

#### Successful Response
- **Status Code**: `307 Temporary Redirect`
- **Headers**:
Location: https://original-url.com

text

#### Error Responses
| Status Code | Reason                      |
|-------------|-----------------------------|
| `404 Not Found` | Short URL doesn't exist    |
| `410 Gone`      | Short URL has expired      |


## Technical Specifications

### Input Validation

1. **URL Format**:
   - Must be valid HTTP/HTTPS URL.
2. **Length Limit**:
   - Maximum length is 2048 characters.
3. **Accessibility Check**:
   - URL must return a `200 OK` status code.
4. **Public Access**:
   - Rejects private/localhost URLs.

### Database Schema

| Column           | Type      | Description                     |
|------------------|-----------|---------------------------------|
| `id`             | String(8) | Primary Key (Short ID)          |
| `original_url`   | Text      | Original URL                    |
| `expiration_date`| DateTime  | Validity period (30 days)       |

