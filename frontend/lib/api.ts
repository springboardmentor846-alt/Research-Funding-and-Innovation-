const API_URL = "http://127.0.0.1:8000";

export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
) {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

  const headers = new Headers(options.headers);

  // Only send JSON content type when a request actually has a body.
  // This avoids unnecessary CORS preflight problems for GET requests.
  if (options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;

  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (error) {
    console.error("API CONNECTION ERROR:", error);

    throw new Error(
      "Cannot connect to backend. Make sure FastAPI is running on http://127.0.0.1:8000"
    );
  }

  let data: any = null;

  const contentType = response.headers.get("content-type");

  if (contentType?.includes("application/json")) {
    data = await response.json();
  } else {
    const text = await response.text();
    data = text ? { detail: text } : null;
  }

  if (!response.ok) {
    console.error("API ERROR:", {
      status: response.status,
      endpoint,
      data,
    });

    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : `Request failed with status ${response.status}`
    );
  }

  return data;
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
  }
}