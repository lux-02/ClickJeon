// utils/vendor-matcher.js
// Loaded as a content script — uses cj prefix to avoid global name collisions

;(function () {
  if (globalThis.__cjVendorMatcherInit) return
  globalThis.__cjVendorMatcherInit = true

  const CJ_VENDORS_URL = typeof chrome !== 'undefined'
    ? chrome.runtime.getURL('data/korean-vendors.json')
    : null

  let _cjVendors = null

  async function _cjLoadVendors() {
    if (_cjVendors) return _cjVendors
    const resp = await fetch(CJ_VENDORS_URL)
    _cjVendors = await resp.json()
    return _cjVendors
  }

  function _cjMatchVendorSync(query, vendors) {
    const q = query.toLowerCase()
    for (const vendor of vendors) {
      const name = vendor.name.toLowerCase()
      const aliases = (vendor.aliases || []).map(a => a.toLowerCase())
      const keywords = (vendor.keywords || []).map(k => k.toLowerCase())
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

  async function cjMatchVendor(query) {
    const vendors = await _cjLoadVendors()
    return _cjMatchVendorSync(query, vendors)
  }

  globalThis.cjMatchVendor = cjMatchVendor
})()
