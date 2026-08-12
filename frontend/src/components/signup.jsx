import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Signup() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleOnClick = async () => {
        try {
            const response = await axios.post("https://cursor-for-2danimation.onrender.com/signup", 
                { username, password, picture: ""},
                { withCredentials: true },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
            navigate("/signin");
        } catch (error) {
            console.error("Signup failed:", error.response?.data || error.message);
        }
    };

    return (
        <div className="bg-black h-screen w-screen flex items-start justify-center ">
            <div className="border border-neutral-700 text-white py-12 px-12 rounded-xl bg-neutral-800 mt-24 text-xl">
                <div className="font-bold text-2xl text-center ">Create your account</div>
                <p className="mb-4 text-sm text-neutral-400">Welcome! Please fill in the details to get started.</p>
                <div className=" flex justify-center">
                    <button className="bg-neutral-800  justify-center hover:bg-neutral-600 text-white border border-neutral-600 flex px-8 py-2 rounded-xl items-center gap-2" 
                    onClick={
                        () => {
                            window.location.href="https://cursor-for-2danimation.onrender.com/login/google";
                    }}>
                        <img src="https://www.citypng.com/public/uploads/preview/google-logo-icon-gsuite-hd-701751694791470gzbayltphh.png" className="w-[20x] h-[20px] rounded-xl "/>
                        <div className="text-center text-md">Google</div>
                    </button>
                </div>
                <div className="flex items-center gap-2 justify-center text-neutral-400 mt-2">
                    <hr className="w-full"></hr>
                    <span className="font-bold">or</span>
                    <hr className="w-full"></hr>
                </div>
                <InputBox text={"Username"} type={"text"} setter={setUsername} />
                <InputBox text={"Password"} type={"password"} setter={setPassword} />
                <div className="text-center mt-4">
                    <button 
                        onClick={handleOnClick} 
                        className="bg-neutral-200 text-black px-6 py-2 rounded-2xl text-xl hover:bg-neutral-400">
                        Sign Up
                    </button>
                </div>
                 <div className="text-sm text-neutral-400 mt-1 text-center">Have an account??<span className="cursor-pointer underline text-blue-400 ml-1" onClick={() => {navigate("/signin")}}>Signin</span></div>
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
                    className="bg-neutral-800 text-white px-2 py-1 border-1 border-neutral-600 rounded-xl w-full"
                />
        </div>
    );
};
