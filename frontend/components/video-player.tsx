"use client"

import { useState, useRef } from "react"
import { Play, Pause } from "lucide-react"

export function VideoPlayer() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const videoRef = useRef<HTMLVideoElement>(null)

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        const p = videoRef.current.play()
        if (p && typeof p.then === "function") {
          p.catch(() => {})
        }
      }
      setIsPlaying(!isPlaying)
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <div className="relative w-full aspect-video rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-cover block"
          playsInline
          preload="auto"
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onLoadedMetadata={(e) => setDuration((e.target as HTMLVideoElement).duration)}
          onTimeUpdate={(e) => setCurrentTime((e.target as HTMLVideoElement).currentTime)}
        >
          <source src="/video.mp4" type="video/mp4" />
        </video>
        <div className={`absolute inset-0 flex items-center justify-center transition-opacity duration-300 ${
          isPlaying ? "opacity-0 pointer-events-none" : "opacity-100"
        }`}>
          <button
            onClick={togglePlay}
            className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center transition-transform duration-300 hover:scale-110"
            aria-label={isPlaying ? "Pause" : "Play"}
          >
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg">
              {isPlaying ? (
                <Pause className="w-8 h-8 text-gray-800" />
              ) : (
                <Play className="w-8 h-8 text-gray-800 ml-1" />
              )}
            </div>
          </button>
        </div>
        <div className="absolute bottom-2 right-2 text-white/80 text-xs bg-black/30 rounded-md px-2 py-1">
          {formatTime(currentTime)} / {formatTime(duration || 0)}
        </div>
      </div>
      <p className="mt-4 text-gray-600 font-medium text-lg">Native Speaker – American English</p>
    </div>
  )
}
