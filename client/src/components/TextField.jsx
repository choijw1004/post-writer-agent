// 입력창. 테두리 대신 배경색 차이로 층을 구분하고, 포커스에서만 파랑이 든다.
export default function TextField({ value, onChange, onEnter, ...props }) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') onEnter?.()
      }}
      className="w-full rounded-2xl border border-line bg-surface px-5 py-4 text-[16px] transition-all duration-200 outline-none placeholder:text-ink-sub focus:border-brand focus:bg-white"
      {...props}
    />
  )
}
