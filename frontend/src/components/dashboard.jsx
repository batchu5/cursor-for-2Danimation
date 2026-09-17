import api, { setTokenGetter } from "../axiosInstance";
import { useEffect, useState } from "react";
import VideoPlayer from "../videoplayer";
import Sidebar from "./sidebar";
import Chat from "./mainLayout";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { newChat } from "../store/newchatAtom";
import { videosAtom } from "../store/videosAtom";
import { conversationClick } from "../store/conversationClick";
import { errorAtom } from "../store/errorAtom";
import { useAuth0 } from "@auth0/auth0-react";
import { generateVideoWithStream } from "../utils/streamHelper";

export default function DashBoard() {
  const { user, getAccessTokenSilently } = useAuth0();
  const videos = useRecoilValue(videosAtom);
  const setVideos = useSetRecoilState(videosAtom)
  const isNewChat = useRecoilValue(newChat)
  const convoClick = useRecoilValue(conversationClick);
  const setConvoClick = useSetRecoilState(conversationClick);
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [currentVideo, setCurrentVideo] = useState([]);
  const error = useRecoilValue(errorAtom);
  const setError = useSetRecoilState(errorAtom); 

  // Set the token getter for axios interceptor
  useEffect(() => {
    setTokenGetter(getAccessTokenSilently);
  }, [getAccessTokenSilently]);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const response = await api.get(`/grouped_by_conversation`);
        setVideos(response.data);
      } catch (err) {
        console.error("Failed to load videos", err);
      }
    };
    fetchVideos();
  }, [isNewChat,currentVideo]);

  useEffect(() => {
    console.log(videos)
    console.log(currentVideo)
  }, [videos])

  
  const handleOnClick = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(false);

    let selectedconversationId = "";
    const keys = Object.keys(convoClick).reverse();
    for (const key of keys) {
      if (convoClick[key] === true) {
        selectedconversationId = videos[key][0].conversationId;
        break;
      }
    }

    await generateVideoWithStream({
      prompt,
      conversationId: selectedconversationId,
      getToken: getAccessTokenSilently,
      onSuccess: (newUrl) => {
        setCurrentVideo((prev) => [...prev, { prompt, url: newUrl, selectedconversationId }]);
        setPrompt("");
      },
      onError: () => {
        setError(true);
      }
    });

    setLoading(false);
  };

   const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); 
      handleOnClick();
    }
  };

  return (
    <div className="bg-neutral-800 w-screen h-screen text-white flex ">
        <Sidebar />
        {isNewChat && <Chat />}

        {!isNewChat && (
          <div className="w-screen overflow-auto custom-scrollbar ">
            <div className="pr-4  pt-4 pb-34">
              {videos.map((video, index) => {
                if (convoClick[index]) {
                  return (
                    <div key={index}>
                      {video.map((vid, i) => (
                        <div key={i}>
                          <div className="flex justify-end">
                                <div className="bg-neutral-200 text-neutral-800 text-mono rounded-xl px-4 py-2 text-start w-[800px] text-xl ">{vid.prompt}</div>
                          </div>
                          <VideoPlayer url={vid.url} />
                        </div>
                      ))}
                      {/* loading spinner */}
                      <div className="text-end flex justify-end ">
                          <div className="flex">
                              <span className={`bg-white text-black rounded-xl flex gap-2 ${loading ? "px-4 py-2" : ""}`}>
                                  {loading && <svg
                              className="animate-spin h-8 w-8 text-purple-500 "
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 24 24"
                              >
                              <circle
                                  className="opacity-25"
                                  cx="12"
                                  cy="12"
                                  r="10"
                                  stroke="currentColor"
                                  strokeWidth="4"
                              ></circle>
                              <path
                                  className="opacity-75"
                                  fill="currentColor"
                                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                              ></path>
                              </svg>}
                                  {`${loading ? "loading..." : ""}`}
                                  
                                  
                              </span>
                          </div> 
                      </div>
                      {/* error */}
                      <div className="text-end flex justify-end ">
                          <div className="flex">
                              <span className={`bg-white text-black rounded-xl flex gap-2 ${error ? "px-4 py-2" : ""}`}>
                                  {error && <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-ban-icon lucide-ban"><circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/></svg>}
                                  {`${error ? "Error while genrating the manim code" : ""}`}
                              </span>
                          </div> 
                      </div>


                      <div className={`text-center fixed bottom-0 flex justify-center items-end  w-full`}>
                          <textarea name="message" rows="5" cols="100" className="rounded-3xl bg-neutral-700 outline-none border-none pl-4 pt-2 text-md mb-4" placeholder="Ask Anything here" onKeyDown={handleKeyDown} onChange={(e) => setPrompt(e.target.value)} value={prompt}>
                                    
                          </textarea>
                          
                      </div>

                    </div>
                  );
                }
                
              })}
            </div>
          </div>
            
          )}

    </div>
  );
}

