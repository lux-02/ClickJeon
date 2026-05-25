import { describe, it, expect, beforeEach } from 'vitest'
import { JSDOM } from 'jsdom'
import '../utils/dom-parser.js'
const { extractQueryFromUrl, extractResultsFromDOM } = globalThis

const MOCK_SERP_HTML = `
<html>
<body>
  <input name="q" value="카카오톡 다운로드" />
  <div id="search">
    <div class="g">
      <a href="https://kakao.com/talk/download">
        <h3>카카오톡 PC 다운로드 - 공식</h3>
      </a>
      <div class="VwiC3b">카카오 공식 사이트에서 카카오톡을 다운로드하세요.</div>
    </div>
    <div class="g">
      <a href="https://kakaotalk-download.net/setup.exe">
        <h3>카카오톡 무료 설치 최신버전</h3>
      </a>
      <div class="VwiC3b">빠른 설치 가능합니다.</div>
    </div>
  </div>
</body>
</html>
`

describe('extractQueryFromUrl', () => {
  it('URL의 q 파라미터에서 쿼리 추출', () => {
    const result = extractQueryFromUrl('https://www.google.com/search?q=%EC%B9%B4%EC%B9%B4%EC%98%A4%ED%86%A1+%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C&hl=ko')
    expect(result).toBe('카카오톡 다운로드')
  })

  it('q 파라미터 없으면 빈 문자열', () => {
    const result = extractQueryFromUrl('https://www.google.com/')
    expect(result).toBe('')
  })
})

describe('extractResultsFromDOM', () => {
  let document

  beforeEach(() => {
    const dom = new JSDOM(MOCK_SERP_HTML, { url: 'https://www.google.com/search?q=test' })
    document = dom.window.document
  })

  it('검색 결과 2개 추출', () => {
    const results = extractResultsFromDOM(document)
    expect(results).toHaveLength(2)
  })

  it('첫 번째 결과 필드 검증', () => {
    const results = extractResultsFromDOM(document)
    expect(results[0].rank).toBe(1)
    expect(results[0].domain).toBe('kakao.com')
    expect(results[0].title).toBe('카카오톡 PC 다운로드 - 공식')
    expect(results[0].snippet).toContain('카카오 공식')
  })

  it('두 번째 결과 domain 추출', () => {
    const results = extractResultsFromDOM(document)
    expect(results[1].domain).toBe('kakaotalk-download.net')
  })

  it('유효하지 않은 URL 결과는 건너뜀', () => {
    const dom = new JSDOM(`
      <div id="search">
        <div class="g"><a href="javascript:void(0)"><h3>test</h3></a></div>
        <div class="g"><a href="https://valid.com"><h3>valid</h3></a></div>
      </div>
    `)
    const results = extractResultsFromDOM(dom.window.document)
    expect(results).toHaveLength(1)
    expect(results[0].domain).toBe('valid.com')
  })
})
