import { Link } from 'react-router-dom'

export default function Logo() {
  return <Link to="/" className="font-['Sora'] text-xl font-bold tracking-[-0.02em] text-white" aria-label="Skillora home">
    Skill<span className="bg-gradient-to-r from-[#8b3dff] to-[#e040c0] bg-clip-text text-transparent">ora</span>
  </Link>
}
