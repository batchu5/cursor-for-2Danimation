import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Signup() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleOnClick = async () => {
        try {
            const response = await axios.post("https://cursor-for-2danimation.onrender.com/signin", 
                { username, password, },
                { withCredentials: true },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
            navigate("/dashboard");
        } catch (error) {
            console.error("Signup failed:", error.response?.data || error.message);
        }
    };

    return (
        <div className="bg-black h-screen w-screen flex items-start  justify-center text-xl text-white">
            <div className="border border-neutral-700 text-neutral-300 py-12 px-12 rounded-xl bg-neutral-800 mt-24 text-xl">
                <div className="font-bold text-2xl text-center ">Signin to Prompt2Anim</div>
                <p className="mb-4 text-sm text-neutral-400">Welcome! Please fill in the details to get started.</p>
                
                <InputBox text={"Username"} type={"text"} setter={setUsername} />
                <InputBox text={"Password"} type={"password"} setter={setPassword} />
                <div className="text-center mt-4">
                    <button 
                        onClick={handleOnClick} 
                        className="bg-neutral-300 text-black px-6 py-2 rounded-2xl text-xl hover:bg-neutral-400">
                        Sign in
                    </button>
                </div>
                <div className="text-sm text-neutral-400 mt-1 text-center">Don't have an account<span className="cursor-pointer underline text-blue-400 ml-1" onClick={() => {navigate("/signup")}}>Signup</span></div>
            </div>
        </div>
    );
}

const InputBox = ({ text, type, setter }) => {
    return (
        <div className="my-2">
            <div className="font-semibold text-md">{text}</div>
                <input 
                    type={type} 
                    onChange={(e) => setter(e.target.value)} 
                    className="bg-neutral-800 text-white px-2 py-1 border-1 border-neutral-600 rounded-xl"
                />
        </div>
    );
};
