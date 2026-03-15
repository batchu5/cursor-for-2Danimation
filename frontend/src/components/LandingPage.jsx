
import { useEffect } from "react";
import Navbar from "./Navbar";
import { Spotlight } from "./Spotlight";


export default function LandingPage(){
    useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
    return <div className="overflow-hidden text-white">
        <div className="relative h-screen w-screen overflow-hidden bg-black/[0.96] antialiased ">
            <Navbar />

            <Spotlight  className={"-top-40 left-0 md:-top-0 md:left-60"} fill={"#ffffff"}/>
            
            <div className="text-white  flex justify-center items-center pt-80">
                <div className="max-w-[700px]">
                    <div className="flex justify-center items-center text-7xl text-center font-bold">
                    <div>
                        🎬 Turn Ideas Into Animations  
                        <span className="bg-purple-400 text-neutral-900 inline-block transform rotate-4 ml-4 py-1">
                        Instantly
                        </span>
                    </div>
                    </div>
                    <div className="text-xl flex items-center justify-center text-neutral-400 text-center mt-8">
                            Just type your prompt, we'll bring it to life with stunning 2D Manim animations. No coding. No hassle. Just prompt!
                    </div>

                </div>
                
            </div>
            <div className="py-40 px-4  text-white text-center">
                <h2 className="text-3xl font-bold mb-10 ">How It Works</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-10 max-w-5xl mx-auto">

                    <div className="bg-neutral-900 p-6 rounded-xl shadow-lg hover:border hover:border-purple-800">
                        <h3 className="text-xl font-semibold mb-2"> Step 1: Enter a Prompt</h3>
                        <p className="text-neutral-400">Describe what you want animated in plain English. No scripting or coding required.</p>
                    </div>

                    <div className="bg-neutral-900 p-6 rounded-xl shadow-lg hover:border hover:border-purple-800">
                        <h3 className="text-xl font-semibold mb-2"> Step 2: Let Manim Work</h3>
                        <p className="text-neutral-400">We convert your prompt into a Python-based Manim script and render it automatically.</p>
                    </div>

                    <div className="bg-neutral-900 p-6 rounded-xl shadow-lg hover:border hover:border-purple-800">
                        <h3 className="text-xl font-semibold mb-2"> Step 3: Watch or Download</h3>
                        <p className="text-neutral-400">Get a smooth 2D animation you can preview, download, or embed anywhere.</p>
                    </div>

                </div>
            </div>

        </div>
        <div className={`flex justify-center w-screen md:h-screen bg-black/[0.96]`}>
            <div>

        
            <div className="  ">
                <h1 className="text-center text-2xl flex">
                    <div className="w-[4px] h-6 bg-neutral-600 inline-block mx-2"></div>
                    <div className="text-neutral-300 ">Prompt: Draw a graph of y = sin(x)</div>
                </h1>
                 <video className='w-[1200px] mt-8' controls autoPlay loop muted>
                    <source src={"https://res.cloudinary.com/dxmkpoe7j/video/upload/v1773555847/SinGraph_c3op1a"} type="video/mp4" />
                    Your browser does not support the video tag.
                </video>
            </div>
            
        </div>
        
        </div>
        <div className="text-center py-20 bg-gradient-to-b from-black to-[#0a0a0a] text-white">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">
                        Bring Your Ideas to Life with Animation
                    </h2>
                    <p className="text-lg text-gray-400 mb-8">
                        The simplest way to turn your thoughts into 2D visuals. Try it now or join the waitlist.
                    </p>
                    <button className="px-6 py-3 bg-white text-black rounded-full hover:bg-gray-200 transition">
                        Join the Waitlist
                    </button>
        </div>

        

        
        
    
    </div>
}
