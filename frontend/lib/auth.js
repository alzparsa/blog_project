const ACCESS_KEY = "accessToken";
const REFRESH_KEY = "refreshToken";

export function saveTokens(accessToken, refreshToken) {
    localStorage.setItem(ACCESS_KEY, accessToken);
    if (refreshToken) {
        localStorage.setItem(REFRESH_KEY, refreshToken);
    }
}

export function getAccessToken() {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken() {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(REFRESH_KEY);
}

export function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
}