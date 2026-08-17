import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function CallbackPage() {
  const { isAuthenticated, isLoading, user, getAccessTokenSilently, error } = useAuth0();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [errorMessage, setErrorMessage] = useState(null);

  // Check for Auth0 error in URL params
  const authError = searchParams.get("error");
  const authErrorDescription = searchParams.get("error_description");

  useEffect(() => {
    // If Auth0 returned an error in URL, show it (don't auto-redirect)
    if (authError) {
      console.error("Auth0 error:", authError, authErrorDescription);
      setErrorMessage(authErrorDescription || authError);
      return;
    }

    // If Auth0 SDK reports an error
    if (error) {
      console.error("Auth0 SDK error:", error.message);
      setErrorMessage(error.message);
      return;
    }

    const syncUser = async () => {
      if (isAuthenticated && user) {
        try {
          const token = await getAccessTokenSilently();
          
          // Sync user profile to backend
          await fetch(
            `${import.meta.env.VITE_USE_LOCAL === "true" 
              ? import.meta.env.VITE_BACKEND_URL_LOCAL 
              : import.meta.env.VITE_BACKEND_URL_DEPLOYED}/auth/sync`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                name: user.name || user.nickname || "",
                email: user.email || "",
                picture: user.picture || "",
              }),
            }
          );
        } catch (err) {
          console.error("Failed to sync user:", err);
        }
        navigate("/dashboard");
      }
    };

    if (!isLoading) {
      if (isAuthenticated) {
        syncUser();
      } else {
        // Not authenticated and not loading — wait a moment then show error
        setTimeout(() => {
          if (!isAuthenticated) {
            setErrorMessage("Authentication failed. Please try again.");
          }
        }, 3000);
      }
    }
  }, [isAuthenticated, isLoading, user, error, authError]);

  if (errorMessage) {
    return (
      <div className="bg-neutral-900 h-screen w-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 max-w-lg px-6">
          <div className="text-red-400 text-2xl font-bold">⚠️ Authentication Error</div>
          <div className="text-neutral-300 text-center text-sm bg-neutral-800 p-4 rounded-xl border border-neutral-700 w-full break-words">
            {errorMessage}
          </div>
          <button 
            onClick={() => navigate("/")}
            className="mt-4 px-6 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral-900 h-screen w-screen flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <svg
          className="animate-spin h-10 w-10 text-purple-400"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <span className="text-neutral-400 text-lg">Signing you in...</span>
      </div>
    </div>
  );
}
