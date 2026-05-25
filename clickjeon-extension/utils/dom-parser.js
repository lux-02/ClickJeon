// utils/dom-parser.js

;(function () {
  if (globalThis.__cjDomParserInit) return
  globalThis.__cjDomParserInit = true

  const CJ_SNIPPET_SELECTORS = ['div.VwiC3b', 'div[data-sncf]', 'span.aCOpRe', 'div.IsZvec']

  function extractQueryFromUrl(url) {
    try {
      return new URL(url).searchParams.get('q') || ''
    } catch {
      return ''
    }
  }

  function _extractText(container, selectors) {
    for (const selector of selectors) {
      const el = container.querySelector(selector)
      if (el?.textContent?.trim()) return el.textContent.trim()
    }
    return ''
  }

  function _findItems(doc) {
    const items = []
    const seenContainers = new WeakSet()
    const seenAdHosts = new Set()

    // 1a. 광고 스캔: [data-text-ad] 컨테이너 — 페이지 어디든 (inline 광고 포함)
    for (const ad of doc.querySelectorAll('[data-text-ad]')) {
      if (items.length >= 30) break
      if (seenContainers.has(ad)) continue

      // data-pcu = 실제 도착 도메인 (Google 추적 URL이 아님)
      const pcuAnchor = ad.querySelector('a[data-pcu]')
      const realUrl = pcuAnchor?.getAttribute('data-pcu')
        || [...ad.querySelectorAll('a[href]')].find(a => {
            try { const h = new URL(a.href).hostname; return h !== 'google.com' && h !== 'www.google.com' } catch { return false }
          })?.href

      if (!realUrl) continue

      let domain
      try {
        const u = new URL(realUrl)
        if (u.hostname === 'google.com' || u.hostname === 'www.google.com') continue
        domain = u.hostname.replace(/^www\./, '')
        if (!domain) continue
      } catch { continue }

      const heading = ad.querySelector('[role="heading"][aria-level="3"], [role="heading"]')
      const title = (heading?.textContent || pcuAnchor?.textContent || '').trim().slice(0, 100)
      if (!title) continue

      seenContainers.add(ad)
      seenAdHosts.add(domain)
      items.push({ url: realUrl, domain, title, container: ad, isAd: true })
    }

    // 1b. 광고 fallback: [data-text-ad]이 없는 광고 컨테이너 대비 — anchor 기반
    for (const adsRoot of [doc.querySelector('#tads'), doc.querySelector('#bottomads')].filter(Boolean)) {
      for (const a of adsRoot.querySelectorAll('a[href]')) {
        if (items.length >= 30) break
        let url, domain
        try {
          const u = new URL(a.href)
          if (u.hostname === 'google.com' || u.hostname === 'www.google.com') continue
          domain = u.hostname.replace(/^www\./, '')
          if (!domain || seenAdHosts.has(domain)) continue
          url = a.href
        } catch { continue }

        const title = (a.getAttribute('aria-label') || a.textContent || '')
          .trim()
          .replace(/^Sponsored result\s*/i, '')
          .trim()
          .slice(0, 100)
        if (!title) continue

        const container = a.closest('[data-text-ad], [data-vcap]')
          || (() => { let el = a.parentElement; while (el?.parentElement && el.parentElement !== adsRoot) el = el.parentElement; return el })()
        if (!container || seenContainers.has(container)) continue

        seenContainers.add(container)
        seenAdHosts.add(domain)
        items.push({ url, domain, title, container, isAd: true })
      }
    }

    // 2. organic 스캔: h3 기반, 컨테이너 dedupe
    const searchRoot = doc.querySelector('#search, #rso') || doc.body
    for (const h3 of searchRoot.querySelectorAll('h3')) {
      if (items.length >= 30) break
      // 광고 영역 안의 h3는 이미 1a/1b에서 처리됨 → 스킵
      if (h3.closest('[data-text-ad], #tads, #bottomads')) continue

      const anchor = h3.closest('a[href]') || h3.querySelector('a[href]')
      if (!anchor) continue
      if (!anchor.href.startsWith('http')) continue

      try {
        const urlObj = new URL(anchor.href)
        if (urlObj.hostname === 'google.com' || urlObj.hostname === 'www.google.com') continue
        const domain = urlObj.hostname.replace(/^www\./, '')
        if (!domain) continue

        const title = h3.textContent.trim()
        if (!title) continue

        const container = h3.closest('div.g, [data-hveid], [data-sokoban-container]')
          || (() => { let el = h3.parentElement; for (let i = 0; i < 5 && el?.parentElement; i++) el = el.parentElement; return el })()

        if (seenContainers.has(container)) continue
        seenContainers.add(container)

        items.push({ url: anchor.href, domain, title, container, isAd: false })
      } catch { continue }
    }

    return items
  }

  function extractResultsFromDOM(doc) {
    return _findItems(doc).map((item, i) => ({
      rank: i + 1,
      url: item.url,
      domain: item.domain,
      title: item.title,
      snippet: (item.container ? _extractText(item.container, CJ_SNIPPET_SELECTORS) : '').slice(0, 200),
      is_ad: item.isAd,
    }))
  }

  function cjExtractSearchData() {
    const query = extractQueryFromUrl(window.location.href)
      || document.querySelector('input[name="q"]')?.value
      || document.querySelector('textarea[name="q"]')?.value
      || ''

    const items = _findItems(document)

    items.forEach((item, i) => {
      item.container?.setAttribute('data-cj-rank', String(i + 1))
    })

    const results = items.map((item, i) => ({
      rank: i + 1,
      url: item.url,
      domain: item.domain,
      title: item.title,
      snippet: (item.container ? _extractText(item.container, CJ_SNIPPET_SELECTORS) : '').slice(0, 200),
      is_ad: item.isAd,
    }))

    return { query: query.trim(), results }
  }

  globalThis.extractQueryFromUrl = extractQueryFromUrl
  globalThis.extractResultsFromDOM = extractResultsFromDOM
  globalThis.cjExtractSearchData = cjExtractSearchData
})()
