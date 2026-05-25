// content/content.js
// Depends on: dom-parser.js (loaded first by manifest)

;(function () {
  if (globalThis.__cjContentInit) return
  globalThis.__cjContentInit = true

  const CJ_GRADE_LABEL = {
    OFFICIAL: '공식 배포처',
    TRUSTED:  '신뢰 플랫폼',
    UNKNOWN:  '미확인',
    WARNING:  '주의',
    DANGER:   '위험',
  }

  const CJ_META_ICON = {
    OFFICIAL: '🔒',
    TRUSTED:  '✓',
    UNKNOWN:  '•',
    WARNING:  '⚠',
    DANGER:   '⚠',
  }

  const CJ_BLUR_TEXT = {
    UNKNOWN: '클릭하면 표시',
    WARNING: '클릭하면 내용 표시',
    DANGER:  '위험 사이트 — 클릭하면 표시',
  }

  const CJ_SNIPPET_SELECTORS = ['div.VwiC3b', 'div[data-sncf]', 'span.aCOpRe', 'div.IsZvec', 'div.p4wth', '.Va3FIb .p4wth']

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'START_ANALYSIS') {
      _runAnalysis()
        .then(() => sendResponse({ success: true }))
        .catch(err => sendResponse({ success: false, error: err.message }))
      return true
    }
  })

  async function _runAnalysis() {
    const { query, results } = cjExtractSearchData()

    if (!query) throw new Error('검색 쿼리를 찾을 수 없습니다')
    if (results.length === 0) throw new Error('검색 결과를 찾을 수 없습니다')

    _showLoadingOverlay(query)
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'ANALYZE',
        payload: { query, results, vendor_match: null },
      })

      if (!response.success) throw new Error(response.error)

      _renderOverlay(response.data)
    } finally {
      _hideLoadingOverlay()
    }
  }

  function _showLoadingOverlay(query) {
    _hideLoadingOverlay()
    _detectColorScheme()

    const overlay = document.createElement('div')
    overlay.id = 'cj-loading-overlay'

    const card = document.createElement('div')
    card.className = 'cj-loading-card'

    const spinner = document.createElement('div')
    spinner.className = 'cj-loading-spinner'

    const text = document.createElement('div')
    text.className = 'cj-loading-text'
    text.textContent = '클릭전이 검색 결과를 검증하고 있습니다'

    const queryEl = document.createElement('div')
    queryEl.className = 'cj-loading-query'
    queryEl.textContent = `"${query}" 분석 중...`

    const hint = document.createElement('div')
    hint.className = 'cj-loading-hint'
    hint.textContent = '결과 확인 전까지 클릭이 차단됩니다'

    card.appendChild(spinner)
    card.appendChild(text)
    card.appendChild(queryEl)
    card.appendChild(hint)
    overlay.appendChild(card)
    document.body.appendChild(overlay)
  }

  function _hideLoadingOverlay() {
    document.getElementById('cj-loading-overlay')?.remove()
  }

  function _renderOverlay(data) {
    _removeExistingOverlay()
    _detectColorScheme()
    _injectBanner(data.official_domain)
    data.results.forEach(result => _applyGrade(result))
  }

  // Google 다크모드는 OS 설정과 무관하게 자체 토글 존재 — body 배경색으로 직접 판단
  function _detectColorScheme() {
    const el = document.querySelector('#rso, #search, body')
    let isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (el) {
      const bg = window.getComputedStyle(el).backgroundColor
      const m = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
      if (m) {
        const lum = (parseInt(m[1]) * 299 + parseInt(m[2]) * 587 + parseInt(m[3]) * 114) / 1000
        isDark = lum < 128
      }
    }
    document.documentElement.dataset.cjTheme = isDark ? 'dark' : 'light'
  }

  function _injectBanner(officialDomain) {
    if (!officialDomain) return

    const banner = document.createElement('div')
    banner.id = 'cj-verdict-banner'

    const icon = document.createElement('span')
    icon.textContent = '🔒'

    const text = document.createElement('span')
    text.textContent = '공식 배포처: '

    const domainEl = document.createElement('span')
    domainEl.className = 'cj-banner-domain'
    domainEl.textContent = officialDomain

    text.appendChild(domainEl)
    text.appendChild(document.createTextNode(' 도메인 결과가 가장 신뢰할 수 있습니다'))
    banner.appendChild(icon)
    banner.appendChild(text)

    const anchor = document.querySelector('#search, #rso, [id="search"]')
    if (anchor) anchor.insertBefore(banner, anchor.firstChild)
  }

  function _applyGrade(result) {
    const container = document.querySelector(`[data-cj-rank="${result.rank}"]`)
    if (!container) return

    const grade = result.grade
    const gradeLow = grade.toLowerCase()

    container.classList.add('cj-card', `cj-card-${gradeLow}`)

    const label = document.createElement('span')
    label.className = `cj-label cj-label--${gradeLow}`
    label.textContent = CJ_GRADE_LABEL[grade] || grade
    container.insertBefore(label, container.firstChild)

    // 제목 요소: organic은 h3, 광고는 [role="heading"]
    const titleEl = container.querySelector('h3, [role="heading"]')
    if (!titleEl) return

    let titleBlock = titleEl
    while (titleBlock.parentElement && titleBlock.parentElement !== container) {
      titleBlock = titleBlock.parentElement
    }

    const meta = document.createElement('div')
    meta.className = `cj-meta cj-meta--${gradeLow}`
    const iconSpan = document.createElement('span')
    iconSpan.textContent = CJ_META_ICON[grade]
    const reasonSpan = document.createElement('span')
    reasonSpan.textContent = result.reason || ''
    meta.appendChild(iconSpan)
    meta.appendChild(reasonSpan)
    container.insertBefore(meta, titleBlock)

    if (grade === 'DANGER') titleEl.style.color = '#c5221f'

    if (grade === 'UNKNOWN' || grade === 'WARNING' || grade === 'DANGER') {
      // 광고는 설명+sublinks+특가 전체를 묶어서 블러 (제목/도메인만 노출)
      const isAd = container.matches('[data-text-ad]')
      const adApplied = isAd && _wrapAdBodyBlur(container, grade)
      if (!adApplied) {
        const snippetEl = _findSnippetEl(container)
        if (snippetEl) _wrapSnipBlur(snippetEl, grade)
      }
    }
  }

  // 광고 컨테이너의 "제목 블록"이 위치한 level을 찾아 그 형제 요소(설명/sublinks/특가)를 묶어 블러
  function _wrapAdBodyBlur(container, grade) {
    const titleEl = container.querySelector('h3, [role="heading"]')
    if (!titleEl) return false

    // titleBlock의 부모가 container의 직계 자식이 되는 level까지 walk-up
    let titleBlock = titleEl
    while (titleBlock.parentElement && titleBlock.parentElement !== container) {
      if (titleBlock.parentElement.parentElement === container) break
      titleBlock = titleBlock.parentElement
    }

    const parent = titleBlock.parentElement
    if (!parent || parent === container) return false

    const siblings = [...parent.children].filter(c => c !== titleBlock && !c.classList.contains('cj-snip-blur'))
    if (siblings.length === 0) return false

    const gradeLow = grade.toLowerCase()
    const wrapper = document.createElement('div')
    wrapper.className = `cj-snip-blur cj-snip-blur--${gradeLow}`

    titleBlock.insertAdjacentElement('afterend', wrapper)
    siblings.forEach(sib => wrapper.appendChild(sib))

    const reveal = document.createElement('div')
    reveal.className = 'cj-snip-reveal'
    reveal.textContent = CJ_BLUR_TEXT[grade]
    wrapper.appendChild(reveal)

    reveal.addEventListener('click', () => {
      wrapper.classList.remove(`cj-snip-blur--${gradeLow}`)
      reveal.remove()
    })

    return true
  }

  function _findSnippetEl(container) {
    for (const sel of CJ_SNIPPET_SELECTORS) {
      const el = container.querySelector(sel)
      if (el?.textContent?.trim()) return el
    }
    return null
  }

  function _wrapSnipBlur(snippetEl, grade) {
    const gradeLow = grade.toLowerCase()

    const wrapper = document.createElement('div')
    wrapper.className = `cj-snip-blur cj-snip-blur--${gradeLow}`
    snippetEl.parentNode.insertBefore(wrapper, snippetEl)
    wrapper.appendChild(snippetEl)

    const reveal = document.createElement('div')
    reveal.className = 'cj-snip-reveal'
    reveal.textContent = CJ_BLUR_TEXT[grade]
    wrapper.appendChild(reveal)

    reveal.addEventListener('click', () => {
      wrapper.classList.remove(`cj-snip-blur--${gradeLow}`)
      reveal.remove()
    })
  }

  function _removeExistingOverlay() {
    _hideLoadingOverlay()
    document.getElementById('cj-verdict-banner')?.remove()
    document.querySelectorAll('.cj-label').forEach(el => el.remove())
    document.querySelectorAll('.cj-meta').forEach(el => el.remove())

    document.querySelectorAll('.cj-snip-blur').forEach(wrapper => {
      const parent = wrapper.parentNode
      ;[...wrapper.children].forEach(child => {
        if (!child.classList.contains('cj-snip-reveal')) {
          parent.insertBefore(child, wrapper)
        }
      })
      wrapper.remove()
    })

    document.querySelectorAll('[data-cj-rank]').forEach(el => {
      el.classList.remove('cj-card', 'cj-card-official', 'cj-card-trusted', 'cj-card-unknown', 'cj-card-warning', 'cj-card-danger')
      const titleEl = el.querySelector('h3, [role="heading"]')
      if (titleEl) titleEl.style.removeProperty('color')
    })

    delete document.documentElement.dataset.cjTheme
  }

  globalThis.__cjRun = _runAnalysis
})()

// 매 주입마다 실행 — storage 트리거 확인 (재주입 시에도 동작해야 함)
chrome.storage.local.get('__cjTrigger').then(({ __cjTrigger }) => {
  if (!__cjTrigger || Date.now() - __cjTrigger > 10000) return
  if (!globalThis.__cjRun) return
  const triggerTs = __cjTrigger
  chrome.storage.local.remove('__cjTrigger')
  globalThis.__cjRun()
    .then(() => chrome.storage.local.set({ __cjResult: { success: true, ts: triggerTs } }))
    .catch(err => chrome.storage.local.set({ __cjResult: { success: false, error: err.message, ts: triggerTs } }))
})
