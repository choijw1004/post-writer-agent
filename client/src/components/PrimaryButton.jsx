// 파랑을 쓰는 유일한 버튼. 한 화면에 하나만 둔다.
export default function PrimaryButton({ children, disabled, ...props }) {
  return (
    <button
      type="button"
      disabled={disabled}
      className="w-full rounded-2xl bg-brand py-4 text-[16px] font-semibold text-white transition-all duration-200 hover:bg-brand-dark active:scale-[0.985] disabled:cursor-not-allowed disabled:bg-line disabled:text-ink-sub"
      {...props}
    >
      {children}
    </button>
  )
}
