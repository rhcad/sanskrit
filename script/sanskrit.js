/**
 * 创建页面元素
 * @param {HTMLElement} parent 添加到哪个元素
 * @param {string} cls 元素类名，多个用空格分隔
 * @param {string} [tag] 标签名
 * @param {object} [attr] 可选的属性，可有 html、text、data_...
 * @returns {HTMLElement}
 */
function createElement(parent, cls, tag='div', attr={}) {
  const element = document.createElement(tag)
  if (cls.trim()) {
    cls.split(/\s+/g).forEach(c => c && element.classList.add(c))
  }
  Object.entries(attr).forEach(([k, v]) => {
    if (v && k === 'html') {
      element.innerHTML = v + ''
    } else if (v && k === 'text') {
      element.textContent = v + ''
    } else if (v) {
      element.setAttribute(k.replace(/_/g, '-'), v + '')
    }
  })
  if (parent) {
    parent.append(element)
  }
  return element
}

const audioHtml = `<button data-idx="@idx" class="audio-button" onclick="toggleAudioButton(this)"><audio src="@dir@idx.mp3?_=${window.audioStamp||1}"></audio></button>`
const sandhiRe = /\([^(),]*(,[^(),]*)+\)/g
const audioRe1 = /▷\d+[a-f]?/g, audioRe2 = /\t*▷/g
const audioNums = []
const puncRe = /^[,?!:]$/
let newWordId = 1
let hasOrgRow = 0
let newSection = null

/**
 * 创建一行元素
 * @param {string} text IAST文本
 * @param {number} rowIndex 行序号
 * @param {object} [options] 选项
 */
function renderRow(text, rowIndex, options={}) {
  if (/[\u0300-\u0305\u0323-\u0324]/.test(text)) {
    console.assert(false, text)
  }
  if (hasBodyCls('show-audio')) {
    text = text.replace(/[:,|] ▷[56]\d\d/g, s => s.replace(' ', ''))
  } else {
    text = text.replace(/\s*▷\d*[a-f]?/g, '')
  }
  if (!text) {
    return
  }

  const splitIdx = text.indexOf(' | ')
  if (splitIdx > 0) {
    const text1 = text.substring(0, splitIdx + 2), remain = text.substring(splitIdx + 3)
    if (!/^▷\d+[a-f]?/.test(remain)) {
      renderRow(text1, rowIndex, options)
      return renderRow(remain, rowIndex + 1, options)
    }
  }
  const iSandhi = options.sandhi === false ? [0, 1] : [-1, undefined]
  const orgHtml = options.sandhi === 'both' && sandhiRe.test(text) && text.replace(
    audioRe1, '').replace(sandhiRe, s => '<b>' + s.substring(1, s.length-1)
    .split(',').slice(0,-1).join('<small>→</small>').replace(/ </g, '<') + '</b>')
  text = text.replace(/\s?-\s?/g, '-').replace(sandhiRe, s => s.substring(1, s.length-1)
    .split(',').slice(iSandhi[0], iSandhi[1]))

  if (/（\d+音节[:）]/.test(text)) {
    Sanscript.si = Sanscript.sn2 = 0
    Sanscript.sn = parseInt(/（(\d+)音节/.exec(text)[1])
    if (/（\d+音节[：:]\s*\d+\+\d+/.test(text)) { // eg: （11音节: 5+6）
      Sanscript.sn2 = parseInt(/音节[：:]\s*(\d+)/.exec(text)[1])
    }
  } else if (/——/.test(text)) {
    Sanscript.si = Sanscript.sn2 = Sanscript.sn = 0
  }
  if (/^#(\d|$)/.test(text)) {
    newSection = createElement(document.getElementById('body'), 'row section')
    if (text.length > 1)
      createElement(newSection, 'sec-title', 'h3', {
        html: (options['sectionRender'] || (s => s))(text.substring(1)),
        onclick: 'toggleSection(this)'
      })
    return
  }

  const row = createElement(newSection || document.getElementById('body'),
    'row' + (/^(\t| {2})/.test(text) ? ' indent' : '') + (rowIndex ? '' : ' title'))

  const devaRow = createElement(row, 'deva-row')
  const iastRow = createElement(row, 'iast-row')
  const audios = [], a = [0, 0];

  if (/^\s*(——|◆)/.test(text)) {
    text = text.replace(/^\s*◆\s*/, '')
    devaRow.classList.add('indent')
    iastRow.classList.add('indent')
    row.style.marginBottom = '0'
  }
  if (options.audioPrefix) {
    text = text.replace(audioRe1, s => audios.push(s.substring(1)) && '▷');
    if (audios.length > 1) {
      row.classList.add('multi-audio')
    }
  }
  const renderIastTexts = (s, i, audio, iastSpan, hasSub, subIndexes) => {
    if (s === '▷') {
      const ele = document.createElement('span'), flag = [];
      ele.innerHTML = _makeAudioButton(options, audios[a[0]], flag);
      if (ele.innerHTML) {
        if (flag[0] === 's') {
          iastSpan.classList.add('has-sentence-voc')
        }
        if (!flag[0] || flag[0] === 's') { // 不是词
          audioNums.push(audios[a[0]])
        } else {
          iastSpan.classList.add('has-word-voc')
        }
        iastSpan.append(ele.firstChild)
      }
      a[0] += 1
      return
    }
    if (puncRe.test(s)) {
      return createElement(iastSpan, 'punc', 'span', {text: s})
    }
    const firstSp = /^[:-]|^$/.test(s) && (!audio || audio[1] === 0)
    if (firstSp) {
      const sp = createElement(iastSpan, 'sp', 'span', {text: s === '' ? ' ' : '-'});
      (sp.closest('.word') || sp).classList.add('has-sp');
      s = s.substring(1)
      if (!s) {
        return
      }
    }
    if (audio ? audio[1] === 0 : firstSp || /-/.test(s) || (hasSub && !wordSpan)) {
      if (options['hoverWord'] !== false) {
        wordSpan = createElement(iastSpan, 'sub-word', 'span',
          {data_id: `${newWordId}-${subIndexes.length}`});
        subIndexes.push(i);
        (wordSpan.closest('.word') || wordSpan).classList.add('has-sub-word')
      }
    }
    i1 += 1
    const clickSection = /^\|{2}\d+\|{2}$/.test(s) && !iastSpan.closest('.word[onclick]')
    let sp = createElement(wordSpan || iastSpan, 'a ' + (i1 % 2 ? 'odd' : 'even'), 'span', {
      data_id: `a${newWordId}-${i}`, data_i: i1,
      html: s.replace(/-/g, '<span class="sp">-</span>')
        .replace(/@\d+/g, t => `<span class="si" end="${ Sanscript.sn2 ? parseInt(t.substring(1))===Sanscript.sn2 || parseInt(t.substring(1))===Sanscript.sn2+1 : parseInt(t.substring(1))===Sanscript.sn}" si="${t.substring(1)}">${t.substring(1)}</span>`),
      onclick: clickSection ? 'toggleSection(this)' : undefined
    });
    sp = sp && sp.querySelector('.sp')
    if (sp) sp.closest('.word').classList.add('has-sp')
    if (audio && audio[1] === audio[2] - 1) {
      _createVocSpan(wordSpan, './voc/', audio[0])
      wordSpan = null
    }
  }

  let words = Sanscript.iastToDevanagari(text, {
    split_aksara: true, removeDevaAudio: hasBodyCls('show-audio') && hasBodyCls('show-iast') && hasBodyCls('show-deva')})
  const orgRow = orgHtml && createElement(row, 'iast-row iast-org', 'div', {html: orgHtml})
  const sentenceAudio = (options['sentenceAudio'] || options['audioAsVoc']) && text.indexOf('▷') > 0
  let i1 = 0, i2 = 0, wordSpan = null

  for (let i = words.length - 1; i >= 0; i--) {
    const w = words[i], c = w[0][0], dash = c === '-'
    if (dash) {
      w[0] = w[0].substring(1)
    }
    if (dash || i > 0) {
      words.splice(i, 0, [dash ? c : '', ''])
    }
  }
  words.forEach(w => {
    const w0 = w[0].replace(audioRe2, '\t▷')
    const iastTexts = w0.split('\t')
    const devaTexts = w[1].replace(audioRe2, '\t▷').split('\t')
    const audioWord = sentenceAudio && /▷/.test(w[0]) ? ' audio-word' : ''
    const spanAttr = {data_id: newWordId, onclick: audioWord ? 'toggleAudioWord(this)' : undefined }
    const devaSpan = createElement(devaRow, 'deva word' + audioWord, 'span', spanAttr)
    const iastSpan = createElement(iastRow, 'iast word' + audioWord, 'span', spanAttr)
    const hasSub = options['hoverWord'] !== false && /-/.test(w[0]), subIndexes = []
    const voc = options['vocAudio'] && hasBodyCls('show-audio') && findVocAudio(w0)

    wordSpan = null
    iastSpan.setAttribute('first-char', w0[0] || '')
    if (voc) {
      let i1 = 0;
      voc.forEach(v => {
        const ws = v[0].split('\t'), audio = v[1]
        const n = ws.length - (ws[ws.length - 1] === '▷' ? 1 : 0)
        ws.forEach((s, i) => {
          renderIastTexts(s, i + i1, audio && [audio, i, n], iastSpan, hasSub, subIndexes)
        })
        i1 += ws.length
      })
    } else {
      if (iastTexts.length === 1 && !iastTexts[0]) {
        iastSpan.classList.remove('audio-word')
        const s1 = createElement(iastSpan, 'sp space', 'span', {html: '&nbsp;'});
        const s2 = createElement(devaSpan, 'sp space', 'span', {html: '&nbsp;'});
        (s1.closest('.word') || s1).classList.add('has-sp');
        (s2.closest('.word') || s2).classList.add('has-sp');
        return
      }
      iastTexts.forEach((s, i) => renderIastTexts(s, i, null, iastSpan, hasSub, subIndexes))
    }
    wordSpan = null
    devaTexts.forEach((s, i) => {
      if (s === '▷') {
        const ele = document.createElement('div'), flag = [];
        ele.innerHTML = _makeAudioButton(options, audios[a[1]], flag)
        a[1] += 1
        return ele.innerHTML && devaSpan.append(ele.firstChild)
      }
      const subIdx = subIndexes.indexOf(i)
      if (subIdx >= 0) {
        wordSpan = createElement(devaSpan, 'sub-word', 'span',
          {data_id: `${newWordId}-${subIdx}`});
        (wordSpan.closest('.word') || wordSpan).classList.add('has-sub-word')
      }
      i2 += 1
      createElement(wordSpan || devaSpan, 'a ' + (i2 % 2 ? 'odd' : 'even'), 'span', {
        data_id: `a${newWordId}-${i}`,
        text: s.replace('——', '—'), data_i: i2
      })
    })
    newWordId++
  })
  if (text.endsWith('-')) {
    createElement(createElement(iastRow, 'iast word'), '', 'span', {text: '-'})
    createElement(createElement(devaRow, 'deva word'), '', 'span', {text: '-'})
  }
  if (orgRow && !hasOrgRow) {
    hasOrgRow = 1
    createElement(orgRow, 'float-right', 'div', {
      html: `<div onclick="_renderBody(true)" class="gray-btn" title="隐藏无连音变化的转写">✕</div>`})
  }
  if (sentenceAudio) {
    const needMerge = hasBodyCls('merge-audio-words')
    let audioWord, prevWord, prev
    for (let word = iastRow.lastChild; word; word = prevWord) {
      prevWord = word.previousSibling
      if (word.classList.contains('audio-word')) {
        audioWord = word
      } else if (audioWord && word.lastChild) {
        if (word.classList.contains('has-sp') && prevWord && prevWord.classList.contains('audio-word')) {
          continue
        }
        if (!needMerge) {
          word.setAttribute('onclick', `toggleAudioWord(this,${audioWord.getAttribute('data-id')})`)
          word.classList.add('audio-word')
          continue
        }
        for (let c = word.lastChild; c; c = prev) {
          prev = c.previousSibling
          audioWord.insertBefore(c, audioWord.firstChild)
        }
        word.remove()
      }
    }
  }
}

function _createVocSpan(wordSpan, dir, idx) {
  const html = audioHtml.replace('@dir', dir)
    .replace(/@idx/g, idx).replace('-button', '-button voc')
  return wordSpan ? createElement(wordSpan, 'voc', 'span', {html: html}) : html
}

function _makeAudioButton(options, idx, flag=null) {
  if (options['sentenceAudio']) {
    if (Array.isArray(flag)) {
      flag[0] = /^[56]\d\d/.test(idx) ? 's' : 'w'
    }
    if (!/^[56]\d\d/.test(idx)) {
      return _createVocSpan(null, options.audioPrefix, idx)
    }
  }
  if (options['audioAsVoc']) {
    return _createVocSpan(null, options.audioPrefix, idx)
  }

  return audioHtml.replace('@dir', options.audioPrefix).replace(/@idx/g, idx)
}

function wordHover(event) {
  const word = event.target.closest && event.target.closest('.word')
  if (word || document.body.querySelector('.hover')) {
    const old = Array.from(document.body.querySelectorAll('.hover'))
    let sub = word && event.target.closest('.sub-word')
    sub = sub || word && !word.querySelector('.sub-word') && word

    if (sub ? old.indexOf(sub) < 0 : old.length) {
      old.forEach(el => el.classList.remove('hover'))
      if (sub) {
        Array.from(document.body.querySelectorAll(`[data-id="${sub.dataset.id}"]`))
          .forEach(el => el.classList.add('hover'))
      }
    }
  }
}

document.addEventListener('mousemove', wordHover)
document.addEventListener('click', wordHover)

function onAudioEnded(e) {
  const btn = e.target.closest('button')
  const curIdx = audioNums.indexOf(btn.dataset.idx)
  let idx = curIdx, nextBtn = []

  btn.classList.remove('playing')
  if (curIdx >= 0 && hasBodyCls('auto-audio')) {
    do {
      idx = (idx + 1) % audioNums.length
      nextBtn = Array.from(document.querySelectorAll(`.audio-button[data-idx="${audioNums[idx]}"]`))
        .filter(b => b.offsetParent)
      if (idx === curIdx)
        return
    } while (!nextBtn.length)

    setTimeout(() => toggleAudioButton(nextBtn[0]),
      idx < curIdx ? 1000 : window.audioGap === undefined ? 100 : window.audioGap)
  }
}

function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return rect.top > 30 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) - 20;
}

function toggleAudioWord(span, aid=0) {
  if (aid && span) {
    span = span.closest('.iast-row,.deva-row')
    span = span.querySelector(`.word[data-id="${aid}"]:has(.audio-button)`)
  }
  const hitSpan = window.event.target
  if (hitSpan && hitSpan.closest('.word') === span) {
    for (let p = hitSpan; p; p = p.nextElementSibling) {
      if (p.classList.contains('audio-button')) {
        return toggleAudioButton(p)
      }
    }
  }
  toggleAudioButton(span.querySelector('.audio-button'))
}

function toggleAudioButton(button) {
  const audio = button && button.firstElementChild || {};
  const btnPlaying = document.querySelector('.playing');

  if (audio.paused) {
    if (btnPlaying) {
      btnPlaying.classList.remove('playing');
      const audio2 = btnPlaying.querySelector('audio');
      if (audio2) {
        audio2.pause();
        audio2.currentTime = 0;
      }
      audio.currentTime = 0;
    }
    audio.onended = audio.onended || onAudioEnded;
    button.classList.add('playing', 'fail');
    audio.play().then(() => button.classList.remove('fail'))
      .catch(e => console.log(e));
    setTimeout(() => {
      if (button.classList.contains('fail') && audioNums.indexOf(button.dataset.idx) >= 0) {
        updateTopBar();
      }
    }, 50);
    if (!isInViewport(button)) {
      const r = button.closest('.row'), p = r.previousElementSibling;
      const el = p && p.lastElementChild || document.querySelector('.title') || button;
      el.scrollIntoView();
    }
  } else if (audio.pause) {
    audio.pause();
    audio.currentTime = 0;
    button.classList.remove('playing', 'fail');
  }
  if (window.event) {
    window.event.stopPropagation()
  }
}

const voc_audios = window.voc_audios || {}
const voc_audio_keys = Object.keys(voc_audios).map(s => s.replace(/-/g, ''))
const _vocRe1 = /\s?-\s?/g, _vocRe2 = /[\t▷]/g, _vocFound = {}

function findVocAudio(word) {
  let ret = null, n = 0
  let w2 = word.replace(_vocRe2, '').replace(_vocRe1, '').replace(/['’]/g, 'a')
  let idx = voc_audio_keys.indexOf(w2)
  if (idx >= 0) {
    n = 1
    _vocFound[idx] = 1
    ret = [[word, Object.values(voc_audios)[idx]]]
  } else if (word.indexOf('-') > 0) {
    ret = word.split(_vocRe1).map((w, i) => {
      w2 = w.replace(_vocRe2, '').replace(/['’]/g, 'a')
      idx = voc_audio_keys.indexOf(w2)
      n += idx >= 0 ? 1 : 0
      w = i ? '-' + w : w
      if (idx >= 0) {
        _vocFound[idx] = 1
      }
      return idx >= 0 ? [w, Object.values(voc_audios)[idx]] : [w, null]
    })
  }
  return n ? ret : null
}

function toggleSection(element) {
  element.closest('.section').classList.toggle('collapse')
}

function hasBodyCls(cls) {
  return document.body.classList.contains(cls)
}
function updateTopBar() {
  Array.from(document.querySelectorAll('#top-bar [data-toggle]'))
    .forEach(btn => btn.classList.toggle('checked',
      hasBodyCls(btn.dataset.toggle)))
}

window._fontSize = window._fontSize || 16
function biggerFont() {
  if (_fontSize < 40) {
    window._fontSize *= 1.05
    document.body.style.fontSize = _fontSize + 'px'
  }
}
function smallerFont() {
  if (_fontSize > 9) {
    window._fontSize *= 0.95
    document.body.style.fontSize = _fontSize + 'px'
  }
}

updateTopBar()
document.getElementById('top-bar').addEventListener('click', function (event) {
  const toggleCls = (event.target.dataset || {}).toggle
  if (toggleCls) {
    document.body.classList.toggle(toggleCls)
    const sandhi = !hasBodyCls('no-sandhi')

    if (toggleCls === 'no-sandhi') {
      if (!sandhi && !event.target.dataset.sandhi) {
        event.target.dataset.sandhi = 'changed'
        document.body.classList.remove('show-deva')
        document.body.classList.remove('show-audio')
      }
      _renderBody(sandhi, toggleCls)
    } else if (['show-audio', 'show-iast', 'show-deva'].indexOf(toggleCls) >= 0) {
      _renderBody(sandhi, toggleCls)
    }
    updateTopBar()
  }
})
window._renderBody = function (sandhi, toggleCls) {
  newSection = null
  audioNums.length = 0
  document.getElementById('body').innerHTML = ''
  window.renderBody(sandhi, toggleCls)
}
