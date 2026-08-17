import axios from "axios";
import { BACKEND_URL } from "./config";

const api = axios.create({
    baseURL: BACKEND_URL,
});

// Token will be set by the Auth0 hook in components
let _getAccessToken = null;

export function setTokenGetter(getter) {
    _getAccessToken = getter;
}

api.interceptors.request.use(async (config) => {
    if (_getAccessToken) {
        try {
            const token = await _getAccessToken();
            config.headers.Authorization = `Bearer ${token}`;
        } catch (err) {
            console.error("Failed to get access token:", err);
            // Redirect to login if token retrieval fails
            window.location.href = "/";
        }
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid — redirect to landing page
            window.location.href = "/";
        }
        return Promise.reject(error);
    }
);

export default api;