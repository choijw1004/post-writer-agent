// 파랑을 쓰는 유일한 버튼. 한 화면에 하나만 둔다.
export default function PrimaryButton({ children, disabled, ...props }) {
  return (
    <button
      type="button"
      disabled={disabled}
      className="w-full rounded-2xl bg-[#48664d] py-4 text-[16px] font-semibold text-white transition-all duration-200 hover:bg-[#3d5441] active:scale-[0.985] disabled:cursor-not-allowed disabled:bg-line disabled:text-ink-sub"
      {...props}
    >
      {children}
    </button>
  )
}
