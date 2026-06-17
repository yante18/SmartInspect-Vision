/**
 * 智检慧眼 — SVG 图标库
 * 24x24 描边风格，通过 CSS currentColor 继承颜色
 * 用法: Icons.scan('20px') 或 Icons.scan('1.2em')
 */

const Icons = (() => {
  const svg = (size, viewBox, inner) =>
    `<svg width="${size}" height="${size}" viewBox="${viewBox}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`;

  return {
    // 导航图标
    scan:      s => svg(s, '0 0 24 24', '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/><line x1="7" y1="3" x2="7" y2="6"/><line x1="17" y1="3" x2="17" y2="6"/>'),
    clipboard: s => svg(s, '0 0 24 24', '<rect x="4" y="3" width="16" height="18" rx="2"/><line x1="8" y1="8" x2="16" y2="8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="18" x2="12" y2="18"/>'),
    car:       s => svg(s, '0 0 24 24', '<path d="M5 17h14M7 17v-6l-2-3h14l-2 3v6"/><circle cx="7" cy="18" r="1.5"/><circle cx="17" cy="18" r="1.5"/><path d="M10 7h4v3h-4z"/>'),
    crosshair: s => svg(s, '0 0 24 24', '<circle cx="12" cy="12" r="9"/><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><circle cx="12" cy="12" r="2"/>'),
    book:      s => svg(s, '0 0 24 24', '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="14" y2="11"/>'),
    cube:      s => svg(s, '0 0 24 24', '<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>'),

    // 功能图标
    camera:    s => svg(s, '0 0 24 24', '<path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/>'),
    upload:    s => svg(s, '0 0 24 24', '<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>'),
    fileText:  s => svg(s, '0 0 24 24', '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/>'),
    refresh:   s => svg(s, '0 0 24 24', '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>'),

    // 状态图标
    alertTriangle: s => svg(s, '0 0 24 24', '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
    checkCircle:  s => svg(s, '0 0 24 24', '<circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-5"/>'),
    xCircle:      s => svg(s, '0 0 24 24', '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'),
    infoCircle:   s => svg(s, '0 0 24 24', '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'),
    alertCircle:  s => svg(s, '0 0 24 24', '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'),

    // 通用图标
    search:    s => svg(s, '0 0 24 24', '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'),
    chevronL:  s => svg(s, '0 0 24 24', '<polyline points="15 18 9 12 15 6"/>'),
    chevronR:  s => svg(s, '0 0 24 24', '<polyline points="9 18 15 12 9 6"/>'),
    trash:     s => svg(s, '0 0 24 24', '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>'),
    mapPin:    s => svg(s, '0 0 24 24', '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>'),
    plus:      s => svg(s, '0 0 24 24', '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>'),
    eye:       s => svg(s, '0 0 24 24', '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>'),
    package:   s => svg(s, '0 0 24 24', '<path d="M16.5 9.4L7.55 4.24"/><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.29 7 12 12 20.71 7"/><line x1="12" y1="22" x2="12" y2="12"/>'),
    database:  s => svg(s, '0 0 24 24', '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>'),
    barChart:  s => svg(s, '0 0 24 24', '<line x1="3" y1="21" x2="3" y2="21"/><line x1="7" y1="15" x2="7" y2="21"/><line x1="11" y1="9" x2="11" y2="21"/><line x1="15" y1="13" x2="15" y2="21"/><line x1="19" y1="5" x2="19" y2="21"/>'),
    server:    s => svg(s, '0 0 24 24', '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>'),

    // 品牌图标
    logoMark: s => svg(s, '0 0 32 32', '<circle cx="16" cy="16" r="14" stroke-width="2.5"/><path d="M16 6v12M10 16h12" stroke-width="2.5"/><circle cx="16" cy="11" r="2.5" fill="currentColor" stroke="none"/>'),

    /**
     * 便捷方法：生成导航链接图标 HTML
     */
    navIcon(name, size) {
      const s = size || '1.15em';
      const icons = { scan: this.scan, clipboard: this.clipboard, car: this.car, crosshair: this.crosshair, book: this.book };
      return icons[name] ? icons[name](s) : '';
    },

    /**
     * 自动扫描页面中所有 [data-icon] 元素并注入 SVG
     * @param {Element} root - 扫描的根元素，默认 document.body
     */
    init(root = document.body) {
      const sizeMap = {
        'nav-icon': '1.15em',
        'btn-icon': '1em',
        'upload-icon-block': '2.8em',
        'empty-icon': '3.5em',
        'title-icon': '1.2em'
      };
      root.querySelectorAll('[data-icon]').forEach(el => {
        if (el.querySelector('svg')) return; // 已有 SVG，跳过
        const name = el.getAttribute('data-icon');
        const cls = Array.from(el.classList).find(c => sizeMap[c]);
        const size = sizeMap[cls || ''] || '1.4em';
        if (typeof Icons[name] === 'function') {
          el.innerHTML = Icons[name](size);
        }
      });
    }
  };
})();

// DOM Ready 时自动初始化图标
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Icons.init());
} else {
  Icons.init();
}

// 监听动态内容变化，自动初始化新添加的图标
if (typeof MutationObserver !== 'undefined') {
  const observer = new MutationObserver(mutations => {
    mutations.forEach(m => {
      m.addedNodes.forEach(node => {
        if (node.nodeType === 1) Icons.init(node);
      });
    });
  });
  
  function startObserve() {
    if (document.body) {
      observer.observe(document.body, { childList: true, subtree: true });
    } else {
      setTimeout(startObserve, 50);
    }
  }
  startObserve();
}

// 全局导出
if (typeof window !== 'undefined') window.Icons = Icons;
