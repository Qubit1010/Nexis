interface Props {
  score: number
  verified: boolean
}

export default function ScoreBadge({ score, verified }: Props) {
  let ring: string
  let text: string
  let bg: string
  let label: string

  if (!verified) {
    ring = 'ring-gray-600/60'
    text = 'text-gray-400'
    bg = 'bg-gray-800/60'
    label = 'unver'
  } else if (score >= 70) {
    ring = 'ring-green-500/60'
    text = 'text-green-400'
    bg = 'bg-green-900/30'
    label = 'strong'
  } else if (score >= 40) {
    ring = 'ring-yellow-500/60'
    text = 'text-yellow-400'
    bg = 'bg-yellow-900/30'
    label = 'ok'
  } else {
    ring = 'ring-red-500/40'
    text = 'text-red-400'
    bg = 'bg-red-900/20'
    label = 'weak'
  }

  return (
    <div className={`w-12 h-12 rounded-full ring-2 flex flex-col items-center justify-center shrink-0 ${ring} ${bg}`}>
      <span className={`text-base font-bold leading-none ${text}`}>{score}</span>
      <span className={`text-[9px] leading-none mt-0.5 ${text} opacity-70`}>{label}</span>
    </div>
  )
}
