// Backend from the uploaded Blog API does not use /api and does not return JWTs.
// Authentication is handled by an HttpOnly cookie named "session_id".
const API_BASE = window.API_BASE || (
  window.location.hostname === "localhost" && window.location.port !== "8000"
    ? "http://127.0.0.1:8000"
    : window.location.hostname === "127.0.0.1" && window.location.port !== "8000"
      ? "http://127.0.0.1:8000"
      : ""
);

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  }[char]));
}

function getPostId() {
  return new URLSearchParams(window.location.search).get("id");
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  });
}

function showMessage(message, type = "error") {
  const box = document.querySelector("#message");
  if (!box) return;
  box.textContent = message;
  box.className = `message ${type}`;
  box.hidden = false;
}

function clearMessage() {
  const box = document.querySelector("#message");
  if (box) box.hidden = true;
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  // Important: the backend authenticates with the session_id cookie.
  // The cookie is HttpOnly, so JavaScript must NOT try to read it.
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include"
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || body.message || message;
    } catch (_) {
      // Response was not JSON.
    }
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}

function requireLogin(error) {
  if (error?.status === 401) {
    window.location.href = "login.html";
    return true;
  }
  return false;
}

function renderPostCards(posts) {
  const grid = document.querySelector("#latest-posts");
  if (!grid) return;

  if (!posts.length) {
    grid.innerHTML = '<div class="empty">No posts found.</div>';
    return;
  }

  grid.innerHTML = posts.map(post => `
    <article class="card">
      <div class="image-placeholder">MyBlog</div>
      <div class="card-body">
        <h3>${escapeHtml(post.title)}</h3>
        <p>${escapeHtml(post.content.slice(0, 120))}${post.content.length > 120 ? "..." : ""}</p>
        <div class="date">${escapeHtml(formatDate(post.created_at))}</div>
        <a class="read-more" href="post.html?id=${post.id}">Read More →</a>
      </div>
    </article>
  `).join("");
}

async function loadHome() {
  const grid = document.querySelector("#latest-posts");
  if (!grid) return;

  try {
    const posts = await api("/posts");
    renderPostCards(posts);
  } catch (error) {
    if (requireLogin(error)) return;
    grid.innerHTML = `<div class="empty">Could not load posts: ${escapeHtml(error.message)}</div>`;
  }
}

function setupLogin() {
  const form = document.querySelector("#login-form");
  if (!form) return;

  form.addEventListener("submit", async event => {
    event.preventDefault();
    clearMessage();

    const email = form.email.value.trim();
    const password = form.password.value;

    try {
      await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });

      // Backend sets the HttpOnly session_id cookie.
      window.location.href = "index.html";
    } catch (error) {
      showMessage(error.message || "Login failed.");
    }
  });
}

function setupRegister() {
  const form = document.querySelector("#register-form");
  if (!form) return;

  form.addEventListener("submit", async event => {
    event.preventDefault();
    clearMessage();

    const email = form.email.value.trim();
    const password = form.password.value;
    const confirm = form.confirm.value;

    if (password !== confirm) {
      showMessage("Passwords do not match.");
      return;
    }

    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });

      showMessage("Registration successful. Redirecting to login...", "success");
      setTimeout(() => window.location.href = "login.html", 700);
    } catch (error) {
      showMessage(error.message || "Registration failed.");
    }
  });
}

function setupCreatePost() {
  const form = document.querySelector("#create-form");
  if (!form) return;

  form.addEventListener("submit", async event => {
    event.preventDefault();
    clearMessage();

    const title = form.title.value.trim();
    const content = form.content.value.trim();

    if (!title || !content) {
      showMessage("Title and content are required.");
      return;
    }

    try {
      await api("/posts", {
        method: "POST",
        body: JSON.stringify({ title, content })
      });
      window.location.href = "my-posts.html";
    } catch (error) {
      if (requireLogin(error)) return;
      showMessage(error.message || "Post could not be published.");
    }
  });
}

async function loadPostPage() {
  const container = document.querySelector("#post-container");
  if (!container) return;

  const postId = getPostId();
  if (!postId) {
    container.innerHTML = '<div class="empty">Post ID is missing.</div>';
    return;
  }

  try {
    const post = await api(`/posts/${postId}`);
    document.title = `${post.title} - MyBlog`;

    container.innerHTML = `
      <h1 class="post-title">${escapeHtml(post.title)}</h1>
      <div class="post-meta">
        <span class="author"><span class="avatar">U</span> User #${post.user_id}</span>
        <span>▣ ${escapeHtml(formatDate(post.created_at))}</span>
      </div>
      <div class="post-hero image-placeholder">MyBlog</div>
      <div class="post-copy">${escapeHtml(post.content).replace(/\n/g, "<br>")}</div>

      <section class="comments">
        <h2>Comments <span id="comment-count"></span></h2>
        <div id="comments-list" class="comment-list"></div>
        <form id="comment-form" class="comment-form">
          <textarea id="comment-content" class="textarea" placeholder="Write your comment..." required></textarea>
          <div class="comment-actions">
            <button class="btn" type="submit">Post Comment</button>
          </div>
        </form>
        <div id="comment-message" class="message" hidden></div>
      </section>
    `;

    await loadComments(postId);
    setupCommentForm(postId);
  } catch (error) {
    if (requireLogin(error)) return;
    container.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
  }
}

async function loadComments(postId) {
  const list = document.querySelector("#comments-list");
  const count = document.querySelector("#comment-count");
  if (!list) return;

  try {
    const comments = await api(`/posts/${postId}/comments`);
    count.textContent = `(${comments.length})`;

    if (!comments.length) {
      list.innerHTML = '<div class="empty">No comments yet. Be the first to comment.</div>';
      return;
    }

    list.innerHTML = comments.map(comment => `
      <article class="comment">
        <div class="comment-head">
          👤 User #${comment.user_id}
          <span class="date">${escapeHtml(formatDate(comment.created_at))}</span>
        </div>
        <p>${escapeHtml(comment.content)}</p>
        <button class="comment-delete" data-comment-id="${comment.id}" type="button">Delete</button>
      </article>
    `).join("");

    document.querySelectorAll(".comment-delete").forEach(button => {
      button.addEventListener("click", async () => {
        if (!confirm("Delete this comment?")) return;
        try {
          await api(`/posts/comments/${button.dataset.commentId}`, { method: "DELETE" });
          await loadComments(postId);
        } catch (error) {
          if (requireLogin(error)) return;
          showCommentMessage(error.message);
        }
      });
    });
  } catch (error) {
    if (requireLogin(error)) return;
    list.innerHTML = `<div class="empty">Could not load comments: ${escapeHtml(error.message)}</div>`;
  }
}

function showCommentMessage(message, type = "error") {
  const box = document.querySelector("#comment-message");
  if (!box) return;
  box.textContent = message;
  box.className = `message ${type}`;
  box.hidden = false;
}

function setupCommentForm(postId) {
  const form = document.querySelector("#comment-form");
  if (!form) return;

  form.addEventListener("submit", async event => {
    event.preventDefault();
    const textarea = document.querySelector("#comment-content");
    const content = textarea.value.trim();
    if (!content) return;

    try {
      await api(`/posts/${postId}/comments`, {
        method: "POST",
        body: JSON.stringify({ content })
      });
      textarea.value = "";
      await loadComments(postId);
    } catch (error) {
      if (requireLogin(error)) return;
      showCommentMessage(error.message);
    }
  });
}

async function loadMyPosts() {
  const list = document.querySelector("#post-list");
  if (!list) return;

  try {
    const posts = await api("/posts");

    if (!posts.length) {
      list.innerHTML = '<div class="empty">No posts found.</div>';
      return;
    }

    list.innerHTML = posts.map(post => `
      <article class="post-row">
        <div class="thumb image-placeholder">MyBlog</div>
        <div>
          <h3>${escapeHtml(post.title)}</h3>
          <div class="date">▣ ${escapeHtml(formatDate(post.created_at))}</div>
          <div class="post-owner">Owner: User #${post.user_id}</div>
        </div>
        <div class="actions">
          <a class="small-btn" href="post.html?id=${post.id}">View</a>
          <a class="small-btn primary" href="edit-post.html?id=${post.id}">Edit</a>
          <button class="small-btn danger delete-post" data-post-id="${post.id}" type="button">Delete</button>
        </div>
      </article>
    `).join("");

    document.querySelectorAll(".delete-post").forEach(button => {
      button.addEventListener("click", async () => {
        if (!confirm("Delete this post?")) return;
        try {
          await api(`/posts/${button.dataset.postId}`, { method: "DELETE" });
          await loadMyPosts();
        } catch (error) {
          if (requireLogin(error)) return;
          alert(error.message);
        }
      });
    });
  } catch (error) {
    if (requireLogin(error)) return;
    list.innerHTML = `<div class="empty">Could not load posts: ${escapeHtml(error.message)}</div>`;
  }
}

async function loadEditPost() {
  const form = document.querySelector("#edit-form");
  if (!form) return;

  const postId = getPostId();
  if (!postId) {
    showMessage("Post ID is missing.");
    return;
  }

  try {
    const post = await api(`/posts/${postId}`);
    form.title.value = post.title;
    form.content.value = post.content;

    form.addEventListener("submit", async event => {
      event.preventDefault();
      clearMessage();

      const title = form.title.value.trim();
      const content = form.content.value.trim();
      if (!title || !content) {
        showMessage("Title and content are required.");
        return;
      }

      try {
        await api(`/posts/${postId}`, {
          method: "PUT",
          body: JSON.stringify({ title, content })
        });
        window.location.href = `post.html?id=${postId}`;
      } catch (error) {
        if (requireLogin(error)) return;
        showMessage(error.message || "Post could not be updated.");
      }
    });
  } catch (error) {
    if (requireLogin(error)) return;
    showMessage(error.message || "Could not load post.");
  }
}

function setupLogout() {
  document.querySelectorAll(".logout-btn").forEach(button => {
    button.addEventListener("click", async event => {
      event.preventDefault();
      try {
        await api("/auth/logout", { method: "POST" });
      } catch (_) {
        // Even if the server session is already gone, go back to the home page.
      }
      window.location.href = "login.html";
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadHome();
  setupLogin();
  setupRegister();
  setupCreatePost();
  loadPostPage();
  loadMyPosts();
  loadEditPost();
  setupLogout();
});
