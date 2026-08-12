import { Download } from 'lucide-react';
import React from 'react';

const VideoPlayer = ({url}) => {
  {if(url == ""){
    return <div>No video yet</div>
  }}
  const cloudinaryUrl = url; 

  return (
    <div className='flex justify-end mt-4 mb-4'>
      <video className='w-[1000px] ' controls>
        <source src={cloudinaryUrl} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      
    </div>
  );
};

export default VideoPlayer;
