import { useRef, useState } from 'react'

// 폴더 선택. input[webkitdirectory] 는 네이티브 폴더 선택창을 띄우고, 고른
// 폴더 안의 파일 목록을 통째로 넘겨준다.
//
// 경로를 타이핑받지 않는 이유가 하나 더 있다. 브라우저는 보안상 실제 경로를
// 알려주지 않기 때문에, 경로를 받아 서버가 읽는 방식은 브라우저와 서버가
// 같은 기계일 때만 성립한다. 여기서는 내용을 직접 읽어 보낸다.
const MD = /\.(md|markdown)$/i

export default function FolderPicker({ value, onPick }) {
  const inputRef = useRef(null)
  const [reading, setReading] = useState(false)
  const [error, setError] = useState(null)

  async function handleChange(event) {
    const picked = Array.from(event.target.files ?? [])
    event.target.value = '' // 같은 폴더를 다시 골라도 change 가 뜨게

    if (picked.length === 0) return

    // webkitRelativePath 는 "폴더명/하위/파일.md" 형태다.
    const folderName = picked[0].webkitRelativePath.split('/')[0] ?? '선택한 폴더'
    const markdowns = picked.filter((file) => MD.test(file.name))

    if (markdowns.length === 0) {
      setError(`${folderName} 안에 마크다운 파일이 없습니다.`)
      onPick(null)
      return
    }

    setError(null)
    setReading(true)
    try {
      const files = await Promise.all(
        markdowns.map(async (file) => ({
          name: file.name,
          content: await file.text(),
        })),
      )
      onPick({ folderName, files })
    } catch {
      setError('파일을 읽지 못했습니다. 다시 선택해 주세요.')
      onPick(null)
    } finally {
      setReading(false)
    }
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        webkitdirectory=""
        directory=""
        multiple
        className="hidden"
        onChange={handleChange}
      />

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={reading}
        className="w-full rounded-2xl border border-dashed border-line bg-surface px-5 py-6 text-center transition-all duration-200 hover:border-[#48664d] hover:bg-[#48664d]/10 active:scale-[0.99] disabled:opacity-60"
      >
        {reading ? (
          <span className="text-[15px] text-ink-sub">읽는 중…</span>
        ) : value ? (
          <>
            <span className="block text-[16px] font-semibold">
              {value.folderName}
            </span>
            <span className="mt-1 block text-[13px] text-ink-sub">
              마크다운 {value.files.length}개 · 다시 고르려면 눌러주세요
            </span>
          </>
        ) : (
          <>
            <span className="block text-[16px] font-semibold">폴더 열기</span>
            <span className="mt-1 block text-[13px] text-ink-sub">
              글이 들어있는 폴더를 고르면 안의 마크다운을 읽습니다
            </span>
          </>
        )}
      </button>

      {error && <p className="mt-3 text-[13px] text-red-600">{error}</p>}
    </div>
  )
}
