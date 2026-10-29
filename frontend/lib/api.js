import axios from "axios";
import { getAccessToken, getRefreshToken, saveTokens, clearTokens  } from "./auth";

let refreshPromise = null;


const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
});

api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,              // success: pass it through untouched

    async (error) => {
        const original = error.config;   // the request that failed

        const isAuthCall =
            original.url === "/auth/login" || original.url === "/auth/refresh-token";

        // Only handle 401s, only retry once, and never for login/refresh themselves
        if (error.response?.status !== 401 || original._retry || isAuthCall) {
            return Promise.reject(error);
        }

        original._retry = true;

        try {
            // If several requests fail at once, they share one refresh call
            if (!refreshPromise) {
                refreshPromise = axios
                    .post(`${process.env.NEXT_PUBLIC_API_URL}/auth/refresh-token`, {
                        refreshToken: getRefreshToken(),
                    })
                    .finally(() => {
                        refreshPromise = null;
                    });
            }

            const res = await refreshPromise;
            saveTokens(res.data.accessToken, res.data.refreshToken);

            return api(original);        // retry; the request interceptor adds the new token
        } catch (refreshError) {
            clearTokens();               // refresh token expired or invalid: log out
            window.location.href = "/login";
            return Promise.reject(refreshError);
        }
    }
);

export default api;