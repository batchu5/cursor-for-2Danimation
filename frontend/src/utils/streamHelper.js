import { BACKEND_URL } from "../config";
import { toast } from "react-toastify";

export async function generateVideoWithStream({
  prompt,
  conversationId,
  getToken,
  onSuccess,
  onError
}) {
  const toastId = toast.info("Initializing video generation...", {
    isLoading: true,
    autoClose: false
  });

  try {
    const token = await getToken();
    const response = await fetch(`${BACKEND_URL}/generate_video`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ prompt, conversationId })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const msg = errData.detail || errData.error || `Server error (${response.status})`;
      toast.update(toastId, {
        render: msg,
        type: "error",
        isLoading: false,
        autoClose: 6000
      });
      if (onError) onError(msg);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let hasSuccess = false;
    let hasError = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const chunks = buffer.split("\n\n");
      buffer = chunks.pop(); // Keep incomplete piece

      for (const chunk of chunks) {
        const line = chunk.trim();
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.replace("data: ", ""));
            if (data.type === "status") {
              toast.update(toastId, {
                render: data.message,
                type: "info",
                isLoading: true,
                autoClose: false
              });
            } else if (data.type === "success") {
              hasSuccess = true;
              toast.update(toastId, {
                render: data.message || "Video generated successfully!",
                type: "success",
                isLoading: false,
                autoClose: 4000
              });
              if (onSuccess) onSuccess(data.data?.url);
            } else if (data.type === "error") {
              hasError = true;
              toast.update(toastId, {
                render: data.message,
                type: "error",
                isLoading: false,
                autoClose: 6000
              });
              if (onError) onError(data.message);
            }
          } catch (e) {
            console.error("Error parsing stream chunk:", e);
          }
        }
      }
    }

    if (!hasSuccess && !hasError) {
      toast.update(toastId, {
        render: "Stream completed without response.",
        type: "warning",
        isLoading: false,
        autoClose: 4000
      });
    }
  } catch (err) {
    console.error("Stream request failed:", err);
    const errorMsg = err.message || "Failed to connect to backend server";
    toast.update(toastId, {
      render: errorMsg,
      type: "error",
      isLoading: false,
      autoClose: 6000
    });
    if (onError) onError(errorMsg);
  }
}
