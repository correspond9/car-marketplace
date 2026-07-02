"use client";

import { useEffect, useRef } from "react";

export function LoginBackgroundVideo() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    video.muted = true;
    void video.play().catch(() => {
      // Some browsers block autoplay until interaction; keep poster overlay visible.
    });
  }, []);

  return (
    <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden>
      <video
        ref={videoRef}
        className="login-bg-video h-full w-full scale-105 object-cover"
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
      >
        <source src="/videos/login-background.mp4" type="video/mp4" />
      </video>
      <div className="absolute inset-0 bg-slate-950/40" />
    </div>
  );
}
