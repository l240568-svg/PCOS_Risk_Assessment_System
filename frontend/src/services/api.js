const API_BASE_URL = import.meta.env.VITE_API_BASE_URL 

let refreshPromise = null;

export function saveTokens(tokens){
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
}

export function clearTokens(){
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
}

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        throw new Error("No refresh token available");
    }

    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
            "content-type": "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const data = await response.json().catch(() => null);

    if(!response.ok){
        clearTokens();
        throw new Error(data?.detail || "Session expired");
    }
    

    saveTokens(data);
     return data.access_token;
}

function getFreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = refreshToken().finally(() => {
      refreshPromise = null;
    });
  }

  return refreshPromise;
}


export async function apiRequest(endpoint, options = {}, allowRefresh = true)
{
 async function sendRequest(token) {
  const headers = new Headers(options.headers || {});

  const originalBody = options.body;

  const isFormData = originalBody instanceof FormData;

  const isJsonObject =
    originalBody !== null &&
    originalBody !== undefined &&
    (
      Array.isArray(originalBody) ||
      Object.prototype.toString.call(originalBody) === "[object Object]"
    );

  const requestBody = isJsonObject
    ? JSON.stringify(originalBody)
    : originalBody;

  if (
    !isFormData &&
    requestBody !== null &&
    requestBody !== undefined &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    body: requestBody,
  });
}

 let accessToken = localStorage.getItem("access_token");
 let response = await sendRequest(accessToken);

 if(response.status === 401 && allowRefresh && accessToken) {
   accessToken = await getFreshAccessToken();
   response = await sendRequest(accessToken);
 }

 const data = await response.json().catch(() => null);

if (!response.ok) {
  const detail = data?.detail;

  if (typeof detail === "string") {
    throw new Error(detail);
  }

  if (Array.isArray(detail)) {
    const message = detail
      .map((error) => {
        const field = error.loc?.at(-1) || "request";
        return `${field}: ${error.msg}`;
      })
      .join("; ");

    throw new Error(message);
  }

  throw new Error("Request failed");
}

return data;
}
