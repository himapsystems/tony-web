"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Plus, Activity, Scissors } from "lucide-react"

export default function AdminDashboard() {
  return (
    <div className="p-6 space-y-6 bg-white h-full border-r">
      <header>
        <h1 className="text-xl font-bold italic text-blue-600 uppercase tracking-tighter">ToniWeb Admin</h1>
        <p className="text-[10px] uppercase font-bold text-slate-400">Painel Pedagógico</p>
      </header>
      <Card className="border-2 shadow-none">
        <CardHeader className="bg-slate-50 border-b p-3">
          <CardTitle className="text-[10px] font-black uppercase">Editor de Conteúdo</CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-4">
          <div className="space-y-2">
            <Label className="text-[10px] font-bold uppercase">Frase do Exercício</Label>
            <Input placeholder="Ex: The bag is big" className="h-9 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-2">
              <Label className="text-[10px] font-bold uppercase">Fonema-Alvo</Label>
              <Input placeholder="/ɪ/" className="h-9 text-sm" />
            </div>
            <div className="space-y-2">
              <Label className="text-[10px] font-bold uppercase">Tipo de Análise</Label>
              <select className="w-full h-9 px-3 rounded-md border text-xs">
                <option value="vowel">Vogal</option>
                <option value="fricative">Fricativa</option>
              </select>
            </div>
          </div>
          <Button className="w-full bg-blue-600 font-bold uppercase text-[10px]">
            <Plus className="mr-2 h-4 w-4" /> Salvar Lição
          </Button>
        </CardContent>
      </Card>
      <Card className="border-2 shadow-none bg-slate-50">
        <CardHeader className="bg-slate-900 text-white p-3">
          <CardTitle className="text-[10px] font-black uppercase flex items-center gap-2">
            <Scissors className="h-3 w-3" /> Calibração (Mini-Praat)
          </CardTitle>
        </CardHeader>
        <CardContent className="p-10 text-center">
          <Activity className="h-8 w-8 mx-auto text-slate-300 mb-2 animate-pulse" />
          <p className="text-[10px] text-slate-400 uppercase font-bold">Aguardando áudio nativo...</p>
        </CardContent>
      </Card>
    </div>
  )
}