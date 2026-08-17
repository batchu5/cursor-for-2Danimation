import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

export default function Navbar(){
    const navigate = useNavigate();
    const { loginWithRedirect, isAuthenticated } = useAuth0();

    return <div className="text-white flex justify-center fixed top-6 md:w-full z-50">
        <div className="flex justify-center gap-6 md:gap-12 ">
            <div className="flex gap-14  text-xl  md:px-12 py-2 rounded-full bg-neutral-700/40 backdrop-blur-md border border-neutral-700">
                <div className="cursor-pointer hover:bg-neutral-700 rounded-full py-1 px-2 md:px-4 " onClick={() => navigate("/")}>Home</div>
                <div className="cursor-pointer hover:bg-neutral-700 rounded-full py-1 px-2 md:px-4 ">Demo</div>
                {isAuthenticated ? (
                    <div 
                        className="cursor-pointer bg-purple-200 text-black rounded-full py-1 px-4 md:px-6 hover:bg-purple-300 font-medium"
                        onClick={() => navigate("/dashboard")}
                    >
                        Dashboard
                    </div>
                ) : (
                    <div 
                        className="cursor-pointer bg-purple-200 text-black rounded-full py-1 px-4 md:px-6 hover:bg-purple-300 font-medium"
                        onClick={() => loginWithRedirect()}
                    >
                        Get Started
                    </div>
                )}
            </div>
        </div>
    </div>
}