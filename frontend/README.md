# MyBlog Frontend — adjusted to the uploaded Blog API

This frontend now matches the backend in `Blog_API.zip`.

## Backend routes used

### Authentication
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`

The backend uses an **HttpOnly `session_id` cookie**, not a JWT/token. Therefore `app.js` uses `credentials: "include"` and does not store a token in `localStorage`.

### Posts
- `POST /posts`
- `GET /posts`
- `GET /posts/{post_id}`
- `PUT /posts/{post_id}`
- `DELETE /posts/{post_id}`

### Comments
- `POST /posts/{post_id}/comments`
- `GET /posts/{post_id}/comments`
- `DELETE /posts/comments/{comment_id}`

## Important backend limitations

1. The backend has no `/api` prefix, so the frontend uses `http://127.0.0.1:8000` by default.
2. `GET /posts` returns **all posts**, even though the page is named `My Posts`. The backend does not currently provide a `GET /my-posts` endpoint or a current-user endpoint, so the frontend cannot reliably filter posts to only the logged-in user's posts. Edit/delete authorization is still enforced by the backend.
3. Post and comment responses contain `user_id`, not the user's email/name, so the frontend displays `User #<id>`.
4. The backend has no image field for posts, so the image areas are placeholders rather than uploaded post images.
5. If the frontend runs on a different origin such as VS Code Live Server (`http://127.0.0.1:5500`), the backend needs CORS configured with `allow_credentials=True` and the frontend origin allowed. The frontend cannot solve server-side CORS by itself.

## Run locally

Start the FastAPI backend first. Then serve this folder with a local static server such as VS Code Live Server. Do not open the HTML with `file://` when testing cookie-based API authentication.

If the backend is deployed, set the API URL before loading the app, for example:

```html
<script>
  window.API_BASE = "https://your-backend-domain.example";
</script>
<script src="app.js"></script>
```
