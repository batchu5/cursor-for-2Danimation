import axios from "axios";

import { BACKEND_URL } from "./config";

const api = axios.create({
    baseURL : BACKEND_URL,
    withCredentials : true
})

api.interceptors.response.use((response) => response, async(error) => {
    const originalRequest = error.config;

    if(error.response?.status == 401 && !originalRequest._retry){

        originalRequest._retry = true;
        try{
            await axios.post(`${BACKEND_URL}/refresh`, {}, {
                withCredentials: true
            })

            return api(originalRequest);
        }catch{
            window.location.href = "/signin";
        }
    }

    return Promise.reject(error);
})


export default api;