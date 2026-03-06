"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface PitchDataPoint {
  time: number
  pitch: number | null
}

interface PitchIntensityChartProps {
  studentData: PitchDataPoint[]
  nativeData: PitchDataPoint[]
}

export function PitchIntensityChart({ studentData, nativeData }: PitchIntensityChartProps) {
  // Combinar os dados para o Recharts (se necessário, ou plotar linhas independentes se os tempos forem muito distintos)
  // Para este MVP, vamos assumir que o Recharts lida bem com múltiplos arrays se formatarmos corretamente ou usarmos Scatter, 
  // mas para LineChart simples, precisamos garantir que as estruturas sejam arrays.
  
  // O backend já manda no formato [{time: x, pitch: y}, ...]
  // Vamos garantir que não seja null/undefined antes de renderizar
  const safeNative = Array.isArray(nativeData) ? nativeData : []
  const safeStudent = Array.isArray(studentData) ? studentData : []

  // Se não houver dados, não renderiza nada para evitar crash
  if (safeNative.length === 0 && safeStudent.length === 0) {
    return <div className="h-full flex items-center justify-center text-muted-foreground">Sem dados de gráfico</div>
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart>
        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
        <XAxis 
          dataKey="time" 
          type="number" 
          domain={['dataMin', 'dataMax']} 
          label={{ value: 'Tempo (s)', position: 'insideBottom', offset: -5 }} 
          hide 
        />
        <YAxis 
          domain={['auto', 'auto']} 
          label={{ value: 'Pitch (Hz)', angle: -90, position: 'insideLeft' }} 
          hide
        />
        <Tooltip 
          labelFormatter={(val) => `Tempo: ${Number(val).toFixed(2)}s`}
          formatter={(value: any) => [`${Math.round(value)} Hz`]} 
        />
        <Legend verticalAlign="top" height={36}/>
        
        {/* Linha do Nativo (Azul/Ciano) */}
        <Line 
          data={safeNative} 
          type="monotone" 
          dataKey="pitch" 
          name="Nativo" 
          stroke="#0ea5e9" 
          strokeWidth={3} 
          dot={false} 
          connectNulls 
        />
        
        {/* Linha do Aluno (Laranja) */}
        <Line 
          data={safeStudent} 
          type="monotone" 
          dataKey="pitch" 
          name="Você" 
          stroke="#f97316" 
          strokeWidth={3} 
          dot={false} 
          connectNulls 
        />
      </LineChart>
    </ResponsiveContainer>
  )
}