import Link from "next/link";

export default function Logo() {
    return (
        <Link href="/" className="font-bold text-xl lowercase tracking-tight rounded px-1 py-1 transition-colors" aria-label="Acraia home">
            acraia
        </Link>
    )
}