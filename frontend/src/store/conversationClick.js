// conversationClickAtom.js
import { atom, selector } from "recoil";
import { videosAtom } from "./videosAtom";

// Step 1: A selector to generate default { 0: false, 1: false, ... }
export const conversationClickDefaultSelector = selector({
  key: "conversationClickDefaultSelector",
  get: ({ get }) => {
    const videos = get(videosAtom); // [[] , []]
    // console.log(videos)
    const defaultState = {};

    videos.forEach((video, index) => {
      defaultState[index] = false;
    });

    return defaultState;
  }
});

// Step 2: Atom that uses the selector for default
export const conversationClick = atom({
  key: "convo",
  default: conversationClickDefaultSelector,
});
