import axios from "axios";
import { useEffect, useState } from "react";
import VideoPlayer from "../videoplayer";
import Sidebar from "./sidebar";
import Chat from "./mainLayout";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { newChat } from "../store/newchatAtom";
import { videosAtom } from "../store/videosAtom";
import { conversationClick } from "../store/conversationClick";
import { userNameAtom } from "../store/usernameAtom";
import { pictureAtom } from "../store/pictureAtom";
import { errorAtom } from "../store/errorAtom";

export default function DashBoard() {
  // const [videos, setVideos] = useState([]); 
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

  const userName = useRecoilValue(userNameAtom);
  const picture = useRecoilValue(pictureAtom);
  const setUserName = useSetRecoilState(userNameAtom);

  const setPicture = useSetRecoilState(pictureAtom);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        
        const response = await axios.get("https://cursor-for-2danimation.onrender.com/grouped_by_conversation", {
          withCredentials: true, 
          headers: {
            "Content-Type": "application/json"
          }

        });
        const user = await axios.get("https://cursor-for-2danimation.onrender.com/userInfo",{withCredentials : true});
        console.log(user.data);
        setUserName(user.data.name);
        if(user.data.picture === "hello guru kosame ra jeeveihtam"){

          setPicture("https://t4.ftcdn.net/jpg/02/29/75/83/360_F_229758328_7x8jwCwjtBMmC6rgFzLFhZoEpLobB6L8.jpg");
        }
        else{
          setPicture(user.data.picture);
        }

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
  //   console.log(convoClick);
  }, [videos])

  
  const handleOnClick = async () => {
    try {
      setLoading(true);
      let selectedconversationId = "";
      const keys = Object.keys(convoClick).reverse();

      for (const key of keys) {
        if (convoClick[key] === true) {
          selectedconversationId = videos[key][0].conversationId;
          break;
        }
      }
      const generateRes = await axios.post(
        "https://cursor-for-2danimation.onrender.com/generate_video",
        { prompt, conversationId: selectedconversationId },
        { withCredentials: true }
      );

      const resData = generateRes.data;

      if (resData.error) {
        console.error("Backend Error:", resData.error);
        // alert(`Failed to generate video: ${resData.error}`);
        setError(true);
      } else if (resData.data?.url) {
        const newUrl = resData.data.url;
        setCurrentVideo((prev) => [...prev, { prompt, url: newUrl, selectedconversationId }]);
        
      } else {
        console.warn("Unexpected backend response:", resData);
        // alert("Something went wrong. Please try again later.");
        setError(true);
      }
      setPrompt("");
    } catch (err) {
      console.error("Unexpected Error:", err);
      // alert("A network or server error occurred.");
      setError(true);
    } finally {
      setLoading(false);
    }
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
        {/* {console.log(newChat)} */}
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
                                  {error && <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-ban-icon lucide-ban"><circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/></svg>}
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

