import { useNavigate } from 'react-router-dom';
export default function Navbar(){
    const navigate = useNavigate()
    return <div className="text-white flex justify-center fixed top-6 md:w-full ">
        <div className="flex justify-center gap-6 md:gap-12 ">
            <div className="flex gap-14  text-xl  md:px-12 py-2 rounded-full bg-neutral-700/40 backdrop-blur-md border border-neutral-700">
                <div className="cursor-pointer hover:bg-neutral-700 rounded-full py-1 px-2 md:px-4 ">Home</div>
                <div className="cursor-pointer hover:bg-neutral-700 rounded-full py-1 px-2 md:px-4 ">Demo</div>
                <div className="flex bg-purple-200 text-black  rounded-full border border-purple-300">
                    <div className="cursor-pointer hover:bg-purple-300 rounded-full py-1 px-2 md:px-4 " onClick={() => {navigate("/signup")}}>Signup</div>
                    <div className="cursor-pointer hover:bg-purple-300 rounded-full py-1 px-2 md:px-4 " onClick={() => {navigate("/signin")}}>Signin</div>
                </div>
                
            </div>
            
        </div>
    </div>
}