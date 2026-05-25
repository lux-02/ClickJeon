// popup/popup.js

const btn = document.getElementById('analyze-btn')
const status = document.getElementById('status')

function setStatus(text, type = '') {
  status.textContent = text
  status.className = type
}

function setLoading(loading) {
  btn.disabled = loading
  btn.textContent = loading ? '분석 중...' : '지금 분석하기'
}

btn.addEventListener('click', async () => {
  setLoading(true)
  setStatus('')

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

    if (!tab?.url?.includes('google.com/search')) {
      setStatus('구글 검색 페이지에서 사용하세요', 'error')
      setLoading(false)
      return
    }

    let response

    // 1차 시도: 이미 주입된 content script의 메시지 리스너로 전송
    try {
      response = await chrome.tabs.sendMessage(tab.id, { type: 'START_ANALYSIS' })
    } catch (e) {
      if (!e.message.includes('Could not establish connection')) throw e

      // 메시지 채널이 죽은 상태(확장 재로드 후)에서도 동작하도록
      // storage 트리거 + 폴링 방식 사용
      const triggerTs = Date.now()
      await chrome.storage.local.remove('__cjResult')
      await chrome.storage.local.set({ __cjTrigger: triggerTs })

      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['utils/dom-parser.js', 'utils/vendor-matcher.js', 'utils/typo-detector.js', 'content/content.js'],
      })
      await chrome.scripting.insertCSS({
        target: { tabId: tab.id },
        files: ['content/overlay.css'],
      })

      // 결과 폴링 (최대 30초)
      const startTime = Date.now()
      while (Date.now() - startTime < 30000) {
        await new Promise(r => setTimeout(r, 200))
        const { __cjResult } = await chrome.storage.local.get('__cjResult')
        if (__cjResult && __cjResult.ts === triggerTs) {
          response = __cjResult
          await chrome.storage.local.remove('__cjResult')
          break
        }
      }
      if (!response) response = { success: false, error: '분석 시간 초과' }
    }

    if (response?.success) {
      setStatus('✓ 분석 완료', 'success')
    } else {
      setStatus(response?.error || '분석 실패', 'error')
    }
  } catch (err) {
    setStatus('오류: ' + err.message, 'error')
  } finally {
    setLoading(false)
  }
})
