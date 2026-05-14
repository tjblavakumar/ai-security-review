const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface ApiResponse<T = unknown> {
  data: T;
  message: string;
  success: boolean;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${API_BASE}${path}`;
  
  // Don't set Content-Type for FormData - browser will set it with boundary
  const headers: HeadersInit = {};
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  
  const res = await fetch(url, {
    headers: { ...headers, ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.detail || err.message || "Request failed");
  }
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) => {
    // Handle FormData separately (for file uploads)
    if (body instanceof FormData) {
      return request<T>(path, { method: "POST", body });
    }
    return request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });
  },
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
