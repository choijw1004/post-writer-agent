export default function ErrorNote({ message }) {
  if (!message) return null

  return (
    <div className="mx-auto max-w-[560px] px-6 pb-16">
      <p className="rounded-2xl bg-red-50 px-5 py-4 text-[14px] leading-[1.6] text-red-600">
        {message}
      </p>
    </div>
  )
}
