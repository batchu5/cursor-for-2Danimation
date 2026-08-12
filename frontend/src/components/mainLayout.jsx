import axios from "axios";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { convoId } from "../store/conversationIdAtom";
import { useEffect, useState } from "react";
import VideoPlayer from "../videoplayer";
import { videosAtom } from "../store/videosAtom";
import { conversationClick } from "../store/conversationClick";

export default function Chat(){
    const conversationId = useRecoilValue(convoId);
    const [prompt, setPrompt] = useState("");
    // const [video, setVideos] = useState([]);
    const video = useRecoilValue(videosAtom);
    const setVideos = useSetRecoilState(videosAtom)
    const [currentVideo, setCurrentVideo] = useState([]);
    const convoClick = useRecoilValue(conversationClick);
    const setConvoClick = useSetRecoilState(conversationClick);
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        setConvoClick(prev => {
            const updated = {...prev};
            for (const key in updated) {
                if (updated[key] === true) {
                updated[key] = false;
                }
            }
            return updated;
        });
   
    }, [video])
    
    const handleOnClick = async () => {
        try {
            setLoading(true)
            const generateRes = await axios.post(
                "https://cursor-for-2danimation.onrender.com/generate_video",
                { prompt, conversationId},
                { withCredentials: true }
            );
            setLoading(false)
            const newUrl = generateRes.data.data.url;
            setCurrentVideo((prev) => [...prev, { prompt, url: newUrl, conversationId }]);
            // console.log(video)
            setPrompt(""); 
        } catch (err) {
            console.error("Error generating or adding video:", err);
        }
  };
   const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); 
      handleOnClick();
    }
  };

    {
        if(currentVideo.length === 0){
            return (
            <div className="h-screen w-screen flex items-center justify-center ">
                

                {/* TextArea */}
                <div className="">
                    <div className="text-4xl text-center mb-4 ">How can I help you today??</div>
                    <div>
                        <textarea name="message" rows="5" cols="75 " className="rounded-3xl bg-neutral-700 outline-none border-none pl-4 pt-2 text-md" placeholder="Ask Anything here" onKeyDown={handleKeyDown} onChange={(e) => setPrompt(e.target.value)} value={prompt}>
                            
                        </textarea>
                    </div>
                </div>

            </div>
            )
        }
        return (
            <div className=" w-screen flex-col justify-end pb-56 pt-4 pr-4 overflow-auto custom-scrollbar">
                {
                    currentVideo.map((video, index) => (

                        <div key={index} className=" relative ">
                            <div className="flex justify-end">
                                <div className="bg-neutral-600 rounded-xl px-4 py-2 text-start w-[800px] text-xl">{video.prompt}</div>
                            </div>
                            <VideoPlayer url={video.url} />
                        </div>
                    ))
                }

                <div className="text-end flex justify-end ">
                    <div className="flex">
                        

                        <span className={`bg-white text-black  rounded-xl flex gap-2 ${loading ? "px-4 py-2" : ""}`}>
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

                <div className="text-center fixed bottom-0 flex justify-center items-end w-full mb-4">
                            
                    <textarea name="message" rows="5" cols="100" className="rounded-3xl bg-neutral-700 outline-none border-none pl-4 pt-2 text-md" placeholder="Ask Anything here" onKeyDown={handleKeyDown} onChange={(e) => setPrompt(e.target.value)} value={prompt}>
                                
                    </textarea>
                </div>
            </div>
      
        )
    }
  
 
    
}