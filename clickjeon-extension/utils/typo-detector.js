// utils/typo-detector.js

;(function () {
  if (globalThis.__cjTypoDetectorInit) return
  globalThis.__cjTypoDetectorInit = true

  function levenshtein(a, b) {
    const m = a.length
    const n = b.length
    const dp = Array.from({ length: m + 1 }, (_, i) =>
      Array.from({ length: n + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0))
    )

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        dp[i][j] =
          a[i - 1] === b[j - 1]
            ? dp[i - 1][j - 1]
            : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
      }
    }

    return dp[m][n]
  }

  function isSuspiciousDomain(domain, officialDomains) {
    for (const official of officialDomains) {
      if (domain === official) return false
      if (levenshtein(domain, official) <= 3) return true

      const stripTld = d => d.replace(/\.[a-z]{2,6}$/, '')
      const domainName = stripTld(domain)
      const officialName = stripTld(official)

      if (levenshtein(domainName, officialName) <= 2) return true
    }

    return false
  }

  globalThis.levenshtein = levenshtein
  globalThis.isSuspiciousDomain = isSuspiciousDomain
})()
