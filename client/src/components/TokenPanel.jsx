// 토큰 사용량. 평소엔 접혀 있고 발표 때만 편다.
//
// 이 앱은 정보를 덜어내는 쪽으로 디자인했지만 단계별 토큰 사용량은 빼지 않는다.
// 대신 메인 흐름 밖으로 밀어내 접어둔다.
export default function TokenPanel({ usage, model }) {
  if (!usage) return null

  return (
    <details className="group rounded-2xl border border-line bg-surface">
      <summary className="flex cursor-pointer list-none items-center justify-between px-6 py-4 text-[14px] text-ink-sub transition-colors duration-200 hover:text-ink">
        <span>
          토큰 사용량 · 누적{' '}
          <span className="font-semibold text-ink">
            {usage.total_tokens.toLocaleString()}
          </span>
        </span>
        <span className="transition-transform duration-200 group-open:rotate-180">
          ⌄
        </span>
      </summary>

      <div className="border-t border-line px-6 py-5">
        <table className="w-full text-[13px] tabular-nums">
          <thead>
            <tr className="text-ink-sub">
              <th className="pb-2 text-left font-normal">단계</th>
              <th className="pb-2 text-right font-normal">input</th>
              <th className="pb-2 text-right font-normal">output</th>
              <th className="pb-2 text-right font-normal">합계</th>
            </tr>
          </thead>
          <tbody>
            {usage.stages.map((s) => (
              <tr key={s.stage} className="border-t border-line/70">
                <td className="py-2">{s.stage}</td>
                <td className="py-2 text-right">
                  {s.prompt_tokens.toLocaleString()}
                </td>
                <td className="py-2 text-right">
                  {s.completion_tokens.toLocaleString()}
                </td>
                <td className="py-2 text-right font-semibold">
                  {s.total_tokens.toLocaleString()}
                </td>
              </tr>
            ))}
            <tr className="border-t border-ink/15 font-semibold">
              <td className="py-2">누적</td>
              <td className="py-2 text-right">
                {usage.total_prompt_tokens.toLocaleString()}
              </td>
              <td className="py-2 text-right">
                {usage.total_completion_tokens.toLocaleString()}
              </td>
              <td className="py-2 text-right">
                {usage.total_tokens.toLocaleString()}
              </td>
            </tr>
          </tbody>
        </table>

        <p className="mt-5 text-[13px] leading-[1.7] text-ink-sub">
          문체 샘플 {usage.sample_titles.length}편을{' '}
          {usage.sample_tokens.toLocaleString()} 토큰으로 잘라 넣었습니다. 원문을
          그대로 넣는 대신 문체 특징으로 압축해서 작가 단계로 넘기기 때문에, 작가의
          input 이 분석가보다 훨씬 적습니다.
        </p>
        <p className="mt-2 text-[13px] text-ink-sub">모델: {model}</p>
      </div>
    </details>
  )
}
