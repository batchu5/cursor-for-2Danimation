import {Clapperboard, LogOut, PanelRightClose, SquarePen} from "lucide-react"
import { useEffect, useState } from "react"
import { useRecoilValue, useSetRecoilState } from "recoil"
import { newChat } from "../store/newchatAtom"
import { convoId } from "../store/conversationIdAtom"
import { v4 as uuidv4 } from 'uuid';
import { videosAtom } from "../store/videosAtom"
import { conversationClick } from "../store/conversationClick"
import { useAuth0 } from "@auth0/auth0-react"

export default function Sidebar(){
    const [sidebar, setSidebar] = useState(true)
    const setNewChat = useSetRecoilState(newChat);
    const newchat = useRecoilValue(newChat);
    const setConversationId = useSetRecoilState(convoId);
    const video = useRecoilValue(videosAtom);
    const convoClick = useRecoilValue(conversationClick);
    const setConvoClick = useSetRecoilState(conversationClick);
    
    // Get user info directly from Auth0
    const { user, logout } = useAuth0();
    const userName = user?.name || user?.nickname || user?.email || "";
    const picture = user?.picture || "https://t4.ftcdn.net/jpg/02/29/75/83/360_F_229758328_7x8jwCwjtBMmC6rgFzLFhZoEpLobB6L8.jpg";

    return (

      
  <>
    {/* Toggle button for small screens */}
    <div className="md:hidden fixed top-2 left-2 z-50">
      <button
        className="bg-neutral-900 p-2 rounded-md"
        onClick={() => setSidebar(!sidebar)}
      >
        <PanelRightClose size={18} />
      </button>
    </div>

    {/* Sidebar */}
    <div
      className={`
        fixed md:relative top-0 left-0 h-full bg-neutral-900 transition-transform duration-300 z-40
        ${sidebar ? "translate-x-0" : "-translate-x-full"}
        md:translate-x-0
        w-[200px] md:min-w-[200px] md:max-w-[200px]
      `}
    >
      <div className="p-2">
        <div className="flex justify-between items-center">
          <Clapperboard size={18} />
          <button className="md:hidden" onClick={() => setSidebar(false)}>
            <PanelRightClose size={18} />
          </button>
        </div>

        {/* New Chat Button */}
        <div
          className="cursor-pointer mt-4 p-2 hover:bg-neutral-800 rounded-xl"
          onClick={() => {
            setNewChat(!newchat);
            const id = uuidv4();
            setConversationId(id);
          }}
        >
          <div className="flex items-center bg-neutral-100 text-black px-4 py-2 rounded-xl">
            <SquarePen size={14} />
            <div className="pl-2 text-sm">New Chat</div>
          </div>
        </div>
        

        {/* Conversation List */}
        {video.map((vid, index) => {
          const firstPrompt =
            Array.isArray(vid) && vid.length > 0 && vid[0]?.prompt
              ? vid[0].prompt
              : `Conversation ${index + 1}`;

          return (
            <div
              key={index}
              className="cursor-pointer py-1 hover:bg-neutral-800 rounded-xl"
              onClick={() => {
                setConvoClick(() => {
                  const newState = {};
                  video.forEach((_, i) => {
                    newState[i] = i === index;
                  });
                  return newState;
                });
                setNewChat(!newChat);
              }}
            >
              <div
                className={`py-2 px-4 text-sm truncate ${
                  convoClick[index]
                    ? "bg-neutral-800 w-full rounded-xl font-medium text-white"
                    : "text-neutral-300"
                }`}
                title={firstPrompt}
              >
                {firstPrompt}
              </div>
            </div>
          );
        })}
      </div>

     
      <div className="absolute bottom-2 left-2 right-2 bg-neutral-800 rounded-xl px-2 py-3">
        <div className="flex items-center gap-2">
          <img
            src={picture}
            alt="User"
            height="22"
            width="22"
            className="rounded-full"
          />
          <span className="overflow-hidden text-ellipsis whitespace-nowrap text-sm flex-1">
            {userName}
          </span>
        </div>
        <button 
          onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          className="mt-2 w-full flex items-center gap-2 text-sm text-neutral-400 hover:text-white hover:bg-neutral-700 rounded-lg px-2 py-1.5 transition-colors"
        >
          <LogOut size={14} />
          <span>Sign out</span>
        </button>
      </div>
    </div>
  </>
);

    
}

