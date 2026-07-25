const API_BASE_URL = import.meta.env.VITE_API_BASE_URL 

let refreshPromise = null;

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
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        throw new Error(data?.detail || "Session expired");
    }
    

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);

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
 async function sendRequest(token){
   const headers = new Headers(options.headers || {});

   if (!(options.body instanceof FormData)) {
    headers.set("content-type", "application/json");
   }

   if (token) {
    headers.set("Authorization", `Bearer ${token}`);
   }

   return fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
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
    throw new Error(data?.detail || "Request failed");
  }

  return data;
}