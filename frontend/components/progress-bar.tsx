import React from "react"

interface ProgressBarProps {
  score: number
}

export function ProgressBar({ score }: ProgressBarProps) {
  const position = `${Math.max(0, Math.min(100, score))}%`;

  return (
    <div className="w-full space-y-2">
      <p className="text-center text-[10px] font-black text-slate-500 uppercase tracking-widest">
        Pronunciation Score
      </p>
      <div className="relative h-7 w-full flex rounded-md overflow-hidden border-2 border-slate-100">
        <div className="flex-1 bg-[#FF4B4B]" /> 
        <div className="flex-1 bg-[#FF85A2]" />
        <div className="flex-1 bg-[#FFD93D]" />
        <div className="flex-1 bg-[#6BCB77]" />
        
        <div className="absolute top-0 h-full transition-all duration-1000 ease-in-out" style={{ left: position }}>
          <div className="w-0 h-0 border-l-[7px] border-l-transparent border-r-[7px] border-r-transparent border-t-[12px] border-t-white -translate-x-1/2 drop-shadow-md" />
          <div className="w-[2px] h-full bg-white/40 -translate-x-1/2" />
        </div>
      </div>
    </div>
  )
}