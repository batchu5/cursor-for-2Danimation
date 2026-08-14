// Backend URL configuration
// Reads from .env file — toggle VITE_USE_LOCAL to switch between local and deployed

const useLocal = import.meta.env.VITE_USE_LOCAL === "true";

export const BACKEND_URL = useLocal
  ? import.meta.env.VITE_BACKEND_URL_LOCAL
  : import.meta.env.VITE_BACKEND_URL_DEPLOYED;
