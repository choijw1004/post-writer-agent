// 선택형 질문 하나. 고르면 바로 다음 단계로 넘어간다.
// '선택 후 다음 버튼'을 두지 않는 이유: 한 화면에 한 가지만 묻기로 했으므로
// 탭 한 번이면 충분하다.
export default function ChoiceList({ options, value, onSelect, hint }) {
  return (
    <div className="space-y-3">
      {options.map((option) => {
        const label = typeof option === 'string' ? option : option.label
        const key = typeof option === 'string' ? option : option.value
        const selected = value === key

        return (
          <button
            key={key}
            type="button"
            onClick={() => onSelect(key)}
            className={`w-full rounded-2xl border px-5 py-4 text-left transition-all duration-200 active:scale-[0.985] ${
              selected
                ? 'border-brand bg-brand-soft'
                : 'border-line bg-white hover:border-ink-sub/40 hover:bg-surface'
            }`}
          >
            <span
              className={`block text-[16px] font-semibold ${
                selected ? 'text-brand-dark' : 'text-ink'
              }`}
            >
              {label}
            </span>
            {hint?.[key] && (
              <span className="mt-1 block text-[13px] text-ink-sub">{hint[key]}</span>
            )}
          </button>
        )
      })}
    </div>
  )
}
