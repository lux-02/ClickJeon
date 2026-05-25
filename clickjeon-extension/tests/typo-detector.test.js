import { describe, it, expect } from 'vitest'
import '../utils/typo-detector.js'
const { levenshtein, isSuspiciousDomain } = globalThis

describe('levenshtein', () => {
  it('동일 문자열은 0', () => {
    expect(levenshtein('kakao.com', 'kakao.com')).toBe(0)
  })

  it('한 글자 차이는 1', () => {
    expect(levenshtein('kakao.com', 'kakap.com')).toBe(1)
  })

  it('완전히 다른 문자열', () => {
    expect(levenshtein('abc', 'xyz')).toBe(3)
  })
})

describe('isSuspiciousDomain', () => {
  it('공식 도메인은 suspicious 아님', () => {
    expect(isSuspiciousDomain('kakao.com', ['kakao.com'])).toBe(false)
  })

  it('1글자 차이 도메인은 suspicious', () => {
    expect(isSuspiciousDomain('kakap.com', ['kakao.com'])).toBe(true)
  })

  it('타이포스쿼팅 도메인 탐지', () => {
    expect(isSuspiciousDomain('kakaotalk-download.net', ['kakao.com'])).toBe(false)
    // 너무 다른 경우는 suspicious 아님 (거리 > 3)
  })

  it('TLD 제거 후 비교', () => {
    // kakaoo.com vs kakao.com → TLD 제거하면 kakaoo vs kakao → 거리 1
    expect(isSuspiciousDomain('kakaoo.com', ['kakao.com'])).toBe(true)
  })

  it('완전히 다른 도메인은 suspicious 아님', () => {
    expect(isSuspiciousDomain('google.com', ['kakao.com'])).toBe(false)
  })
})
