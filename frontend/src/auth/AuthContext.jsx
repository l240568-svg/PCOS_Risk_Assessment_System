import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { AuthContext } from "./auth-context";

import {
  apiRequest,
  clearTokens,
  saveTokens,
} from "../services/api";


export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearSession = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    const profile = await apiRequest("/users/me");
    setUser(profile);
    return profile;
  }, []);

  useEffect(() => {
    let active = true;

    async function restoreSession() {
      const accessToken = localStorage.getItem("access_token");
      const refreshToken = localStorage.getItem("refresh_token");

      if (!accessToken && !refreshToken) {
        if (active) {
          setIsLoading(false);
        }

        return;
      }

      try {
        const profile = await apiRequest("/users/me");

        if (active) {
          setUser(profile);
        }
      } catch {
        if (active) {
          clearSession();
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    restoreSession();

    return () => {
      active = false;
    };
  }, [clearSession]);

  const login = useCallback(
    async (email, password) => {
      // FastAPI OAuth2PasswordRequestForm expects form fields.
      const loginForm = new FormData();
      loginForm.set("username", email);
      loginForm.set("password", password);

      const tokens = await apiRequest(
        "/auth/login",
        {
          method: "POST",
          body: loginForm,
        },
        false, // Failed login must not trigger token refresh.
      );

      saveTokens(tokens);

      try {
        return await refreshUser();
      } catch (error) {
        clearTokens();
        throw error;
      }
    },
    [refreshUser],
  );

  const register = useCallback(
    (doctorData) =>
      apiRequest(
        "/auth/register",
        {
          method: "POST",
          body: JSON.stringify(doctorData),
        },
        false,
      ),
    [],
  );

  const logout = useCallback(async () => {
    try {
      if (localStorage.getItem("access_token")) {
        await apiRequest("/auth/logout", {
          method: "POST",
        });
      }
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshUser,
    }),
    [
      user,
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    ],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
