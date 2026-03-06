"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Mic, Square, ChevronRight, ChevronLeft, Loader2 } from "lucide-react"
import { PitchIntensityChart } from "./pitch-intensity-chart"
import { ProgressBar } from "./progress-bar" 

// --- TIPAGEM E DADOS ---
type LessonType = "vowel" | "fricative"

interface Lesson {
  id: string
  text: string
  phoneme: string
  type: LessonType
  videoUrl: string
}

const LESSONS: Lesson[] = [
  { id: "ae", text: "The black cat sat on the bag.", phoneme: "æ", type: "vowel", videoUrl: "https://toniweb.b-cdn.net/21.mp4" },
  { id: "ih", text: "The bag is big.", phoneme: "ɪ", type: "vowel", videoUrl: "https://toniweb.b-cdn.net/63.mp4" },
  { id: "th_un", text: "Throw three strong sticks.", phoneme: "θ", type: "fricative", videoUrl: "https://toniweb.b-cdn.net/65.mp4" },
  { id: "sh", text: "The vision was sharp.", phoneme: "ʒ", type: "fricative", videoUrl: "https://toniweb.b-cdn.net/47.mp4" },
  { id: "h", text: "Sam had a bad plan.", phoneme: "h", type: "fricative", videoUrl: "https://toniweb.b-cdn.net/22.mp4" }
]

export default function PronunciationPractice() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  
  const currentLesson = LESSONS[currentIndex]

  // --- NAVEGAÇÃO ---
  const nextLesson = () => {
    setCurrentIndex((prev) => (prev + 1) % LESSONS.length)
    setAnalysisResult(null)
  }

  const prevLesson = () => {
    setCurrentIndex((prev) => (prev - 1 + LESSONS.length) % LESSONS.length)
    setAnalysisResult(null)
  }

  // --- LÓGICA DE GRAVAÇÃO E ENVIO ---
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Configuração para compatibilidade mobile (Safari/Chrome) 
      mediaRecorderRef.current = new MediaRecorder(stream)
      chunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/wav" })
        await sendToBackend(audioBlob)
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setAnalysisResult(null)
    } catch (err) {
      console.error("Erro mic:", err)
      alert("Por favor, permita o uso do microfone para praticar.")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      // Encerra as tracks para liberar o hardware do microfone 
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
    }
  }

  const sendToBackend = async (blob: Blob) => {
    setIsLoading(true)
    const formData = new FormData()
    formData.append("file", blob, "recording.wav")
    formData.append("target_text", currentLesson.text)
    formData.append("target_phoneme", currentLesson.phoneme)
    formData.append("target_type", currentLesson.type)

    try {
      // Endpoint local do FastAPI conforme arquitetura [cite: 2, 12]
      const response = await fetch("http://127.0.0.1:8000/analyze", { 
        method: "POST", 
        body: formData 
      })

      if (!response.ok) throw new Error("Erro no servidor")

      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error("Erro no processamento acústico:", error)
      alert("Erro na conexão com o servidor de análise.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-white max-w-md mx-auto relative overflow-hidden shadow-xl border-x">
      
      {/* 1. VÍDEO (DISTRIBUIÇÃO VIA BUNNYCDN) [cite: 4, 7] */}
      <div className="w-full aspect-video bg-black sticky top-0 z-20 border-b">
        <video 
          key={currentLesson.videoUrl}
          src={currentLesson.videoUrl} 
          controls 
          className="w-full h-full object-cover"
          playsInline
        />
      </div>

      <div className="flex-1 p-4 pb-32 space-y-6 overflow-y-auto">
        
        {/* 2. CONTROLES DE NAVEGAÇÃO */}
        <div className="flex items-center justify-between bg-slate-100 p-2 rounded-xl border">
          <Button variant="ghost" size="icon" onClick={prevLesson}><ChevronLeft className="h-5 w-5"/></Button>
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">
              Alvo: {currentLesson.phoneme}
            </p>
          </div>
          <Button variant="ghost" size="icon" onClick={nextLesson}><ChevronRight className="h-5 w-5"/></Button>
        </div>

        {/* 3. GRÁFICO E FRASE (SCROLL SINCRONIZADO)  */}
        <Card className="p-4 border-2 shadow-sm overflow-hidden bg-slate-50/50">
          <div className="overflow-x-auto scrollbar-hide">
            <div className="min-w-[500px] space-y-4">
              <div className="h-44 w-full flex items-center justify-center bg-white rounded-lg border border-dashed border-slate-200">
                {isLoading ? (
                   <div className="flex flex-col items-center gap-2">
                     <Loader2 className="animate-spin text-blue-500 h-8 w-8" />
                     <span className="text-[10px] font-bold uppercase text-slate-400">Analisando Praat...</span>
                   </div>
                ) : analysisResult ? (
                  <PitchIntensityChart 
                    studentData={analysisResult.details?.student_pitch}
                    nativeData={analysisResult.details?.native_pitch}
                  />
                ) : (
                  <p className="text-xs text-slate-300 uppercase font-black tracking-widest italic">Aguardando Voz</p>
                )}
              </div>
              
              {/* Mapeamento horizontal da frase */}
              <div className="flex justify-between px-2 pt-2 border-t border-slate-200">
                {currentLesson.text.split(" ").map((word, i) => (
                  <span key={i} className="text-[10px] font-black text-slate-500 uppercase font-mono italic">
                    {word}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* 4. SCORE E FEEDBACK VISUAL [cite: 14] */}
        {analysisResult && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-3 duration-500">
            <ProgressBar score={analysisResult.score} />
            <div className={`p-4 rounded-xl text-center border-2 ${
              analysisResult.score >= 75 
              ? 'bg-green-50 border-green-200 text-green-700' 
              : 'bg-red-50 border-red-200 text-red-700'
            }`}>
              <p className="text-xs font-bold leading-relaxed">"{analysisResult.feedback}"</p>
            </div>
          </div>
        )}
      </div>

      {/* 5. BOTÃO DE CAPTURA MOBILE (FIXO)  */}
      <div className="fixed bottom-0 left-0 right-0 p-6 flex justify-center z-30 pointer-events-none bg-gradient-to-t from-white via-white/80 to-transparent">
        <Button
          size="lg"
          className={`h-20 w-20 rounded-full shadow-2xl pointer-events-auto border-4 border-white transition-transform active:scale-95 ${
            isRecording ? "bg-red-500 animate-pulse hover:bg-red-600" : "bg-blue-600 hover:bg-blue-700"
          }`}
          onClick={isRecording ? stopRecording : startRecording}
        >
          {isRecording ? <Square className="h-8 w-8 fill-current text-white" /> : <Mic className="h-10 w-10 text-white" />}
        </Button>
      </div>
    </div>
  )
}