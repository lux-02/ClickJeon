import { describe, it, expect } from 'vitest'
import { readFileSync } from 'fs'
import { resolve } from 'path'

const vendors = JSON.parse(
  readFileSync(resolve('data/korean-vendors.json'), 'utf8')
)

function matchVendorWithData(query, vendorList) {
  const q = query.toLowerCase()
  for (const vendor of vendorList) {
    const name = vendor.name.toLowerCase()
    const aliases = vendor.aliases.map(a => a.toLowerCase())
    const keywords = vendor.keywords.map(k => k.toLowerCase())
    if (
      q.includes(name) ||
      aliases.some(a => q.includes(a)) ||
      keywords.some(k => q.includes(k))
    ) {
      return { id: vendor.id, official_domains: vendor.official_domains }
    }
  }
  return null
}

describe('matchVendor', () => {
  it('카카오톡 키워드로 벤더 매칭', () => {
    const result = matchVendorWithData('카카오톡 다운로드', vendors)
    expect(result).not.toBeNull()
    expect(result.id).toBe('kakaotalk')
    expect(result.official_domains).toContain('kakao.com')
  })

  it('대소문자 구분 없이 매칭', () => {
    const result = matchVendorWithData('KakaoTalk download', vendors)
    expect(result).not.toBeNull()
    expect(result.id).toBe('kakaotalk')
  })

  it('alias로 매칭', () => {
    const result = matchVendorWithData('카톡 pc버전', vendors)
    expect(result).not.toBeNull()
    expect(result.id).toBe('kakaotalk')
  })

  it('등록되지 않은 소프트웨어는 null 반환', () => {
    const result = matchVendorWithData('알 수 없는 프로그램 설치', vendors)
    expect(result).toBeNull()
  })

  it('PuTTY 매칭', () => {
    const result = matchVendorWithData('putty 다운로드', vendors)
    expect(result).not.toBeNull()
    expect(result.id).toBe('putty')
  })
})
