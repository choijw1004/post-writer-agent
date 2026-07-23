// 입력창. 테두리 대신 배경색 차이로 층을 구분하고, 포커스에서만 파랑이 든다.
// prefix 는 velog 의 '@' 처럼 사용자가 굳이 타이핑할 필요 없는 기호를 위한 것.
export default function TextField({ value, onChange, onEnter, prefix, ...props }) {
  const input = (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') onEnter?.()
      }}
      className={
        prefix
          ? 'w-full bg-transparent text-[16px] outline-none placeholder:text-ink-sub'
          : 'w-full rounded-2xl border border-line bg-surface px-5 py-4 text-[16px] transition-all duration-200 outline-none placeholder:text-ink-sub focus:border-brand focus:bg-white'
      }
      {...props}
    />
  )

  if (!prefix) return input

  return (
    <div className="flex items-center gap-1 rounded-2xl border border-line bg-surface px-5 py-4 transition-all duration-200 focus-within:border-brand focus-within:bg-white">
      <span className="text-[16px] text-ink-sub">{prefix}</span>
      {input}
    </div>
  )
}
