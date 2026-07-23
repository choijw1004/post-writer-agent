export default function BackButton({ onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="fixed top-6 left-6 rounded-xl px-3 py-2 text-[15px] text-ink-sub transition-colors duration-200 hover:text-ink"
    >
      ← 이전
    </button>
  )
}
