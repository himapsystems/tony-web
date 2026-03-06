"use client"
import { useState, useEffect } from "react"
import PronunciationPractice from "@/components/pronunciation-practice"
import AdminDashboard from "@/components/admin-dashboard"

export default function Home() {
  const [user, setUser] = useState<{ name: string; isAdmin: boolean } | null>(null)

  useEffect(() => {
    const savedName = localStorage.getItem("toniweb_user")
    const isAdmin = localStorage.getItem("toniweb_admin") === "true"
    if (savedName) setUser({ name: savedName, isAdmin })
  }, [])

  const handleLogin = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const name = formData.get("username") as string
    
    // Auth Mínima: 'admin' ativa o painel pedagógico
    if (name.toLowerCase() === "admin") {
      localStorage.setItem("toniweb_user", "Professor")
      localStorage.setItem("toniweb_admin", "true")
      setUser({ name: "Professor", isAdmin: true })
    } else {
      localStorage.setItem("toniweb_user", name)
      localStorage.setItem("toniweb_admin", "false")
      setUser({ name, isAdmin: false })
    }
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <form onSubmit={handleLogin} className="bg-slate-800 p-8 rounded-xl border border-slate-700 w-full max-w-md shadow-2xl">
          <h1 className="text-3xl font-black text-blue-500 mb-2 text-center italic tracking-tighter uppercase">TONIWEB</h1>
          <p className="text-slate-400 text-[10px] mb-6 text-center uppercase tracking-[0.2em] font-bold">Identificação Simplificada</p>
          <input 
            name="username" 
            placeholder="Digite seu nome ou 'admin'" 
            className="w-full p-4 mb-6 rounded bg-slate-700 text-white outline-none focus:ring-2 focus:ring-blue-500 font-bold" 
            required 
          />
          <button className="w-full bg-blue-600 hover:bg-blue-500 p-4 rounded font-black text-white uppercase tracking-widest transition-all">
            Iniciar Prática
          </button>
        </form>
      </main>
    )
  }

  return (
    <div className={user.isAdmin ? "flex h-screen w-screen bg-slate-100 overflow-hidden" : "min-h-screen bg-white"}>
      {user.isAdmin && (
        <aside className="w-[450px] h-full overflow-y-auto shadow-2xl z-10">
          <AdminDashboard />
        </aside>
      )}
      <main className={user.isAdmin ? "flex-1 h-full flex items-center justify-center bg-slate-200 p-8" : "w-full"}>
        <div className={user.isAdmin ? "w-[375px] h-[750px] bg-white rounded-[3rem] border-[12px] border-slate-900 shadow-2xl overflow-hidden relative" : "w-full"}>
          <PronunciationPractice />
        </div>
      </main>
    </div>
  )
}