/* villafaras 個別ページの共通描画 ----------------------------------------
   iPad Safari 対応: ES5 構文のみ / 外部ライブラリ不使用

   **286ページの HTML にデータを書かない。** spec-data.js（施設スペック）と
   data/villas-lite.js（施設名・県・タグ・価格）から、この 1 本で
   ・SAUNA AT A GLANCE（サウナ要約）
   ・サウナ → 水風呂 → 外気浴 の体験動線
   ・似たサウナのヴィラ
   ・スマートフォンの固定CTA
   を描く。サウナ情報を足したら spec-data.js を直すだけで全ページに出る。

   読み込み順: spec-data.js → spec.js → data/villas-lite.js → villa.js
   （spec.js が window.VILLAFARAS_SPEC_OPTIONS / _SCHEMA を公開する）
--------------------------------------------------------------------------- */
(function () {
  'use strict';

  var SPEC = window.VILLAFARAS_SPEC || {};
  var O    = window.VILLAFARAS_SPEC_OPTIONS || {};
  var LITE = window.VILLAFARAS_LITE || [];

  var PREF_JP = {
    yamanashi: '山梨', kanagawa: '神奈川', shizuoka: '静岡', chiba: '千葉',
    nagano: '長野', tochigi: '栃木', ibaraki: '茨城', gunma: '群馬', saitama: '埼玉'
  };
  var TAG_JP = {
    sauna: 'サウナ', onsen: '温泉', rotenburo: '露天風呂', pet: 'ペットOK',
    pool: 'プール', bbq: 'BBQ', group: '大人数', sea: '海', lake: '湖',
    river: '川', mountain: '山'
  };

  function esc(t) {
    return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /* spec-data.js のセルは { v, src, at, url } か素の値。値だけ取る */
  function val(id, key) {
    var row = SPEC[String(id)];
    if (!row) return null;
    var c = row[key];
    if (c === undefined || c === null || c === '') return null;
    if (typeof c === 'object' && c !== null && 'v' in c) c = c.v;
    if (c === undefined || c === null || c === '') return null;
    return c;
  }

  /* 選択肢は spec.js のマスタで日本語にする。**手で写さない** */
  function label(key, opt) {
    var v = val(key.id, key.k);
    if (v === null) return null;
    if (opt && O[opt] && O[opt][v] !== undefined) return O[opt][v];
    if (v === true) return 'あり';
    if (v === false) return 'なし';
    return String(v);
  }

  /* ---------------------------------------------------------------
     1. SAUNA AT A GLANCE
     値がある項目だけ、細い縦線で区切って並べる。「不明」は出さない。
  --------------------------------------------------------------- */
  function glanceHTML(id) {
    var ex = val(id, 'sauna_exists');
    if (ex === 'no' || ex === null) return '';   /* サウナが無い・未確認なら出さない */

    var k = { id: id, k: '' };
    var bits = [], t;

    k.k = 'sauna_type';  t = label(k, 'saunatype'); if (t) bits.push(t);
    k.k = 'stove';       t = label(k, 'stove');     if (t) bits.push(t);
    t = val(id, 'sauna_temp');  if (t) bits.push(t + '℃');
    k.k = 'loyly';       t = label(k, 'loyly');
    if (t && t !== '不可') bits.push(t === '可' ? 'セルフロウリュ可' : t);
    t = val(id, 'sauna_cap');   if (t) bits.push('定員' + t + '名');

    var cb = val(id, 'coldbath');
    if (cb && cb !== 'none') {
      k.k = 'coldbath'; t = label(k, 'coldbath');
      var wt = val(id, 'water_temp');
      k.k = 'water_temp'; var wtl = wt ? label(k, 'wtemp') : null;
      bits.push(t + (wtl ? ' ' + wtl : ''));
    }
    if (val(id, 'outdoor_rest') === 'yes') bits.push('外気浴');

    if (bits.length < 2) return '';   /* 1項目だけなら要約にならない */

    var out = '<div class="glance-h"><b>サウナ</b><span>SAUNA AT A GLANCE</span></div><div class="glance-row">';
    for (var i = 0; i < bits.length; i++) {
      out += '<span class="glance-i">' + esc(bits[i]) + '</span>';
    }
    return out + '</div>';
  }

  /* ---------------------------------------------------------------
     2. サウナ → 水風呂 → 外気浴 の体験動線
     3段そろって初めて意味があるので、2段以上そろった施設にだけ出す。
  --------------------------------------------------------------- */
  function step(title, en, rows) {
    var body = '', i;
    for (i = 0; i < rows.length; i++) {
      body += '<div class="flow-v' + (i ? '' : ' flow-v1') + '">' + esc(rows[i]) + '</div>';
    }
    return '<div class="flow-step"><div class="flow-h"><b>' + esc(title) +
           '</b><span>' + esc(en) + '</span></div>' + body + '</div>';
  }

  function flowHTML(id) {
    var k = { id: id, k: '' }, t, steps = 0, out = '';

    var a = [];
    /* O.stove の値は既に「電気ストーブ」等なので語を足さない */
    k.k = 'stove';      t = label(k, 'stove');     if (t) a.push(t);
    k.k = 'sauna_type'; t = label(k, 'saunatype'); if (t) a.push(t);
    t = val(id, 'sauna_temp'); if (t) a.push(t + '℃');
    k.k = 'loyly';      t = label(k, 'loyly');
    if (t && t !== '不可') a.push(t === '可' ? 'セルフロウリュ可' : t);
    if (a.length) { out += step('サウナ', 'SAUNA', a); steps++; }

    var b = [];
    k.k = 'coldbath'; t = label(k, 'coldbath'); if (t && t !== 'なし') b.push(t);
    k.k = 'water_temp'; t = label(k, 'wtemp'); if (t) b.push(t);
    k.k = 'water_src';  t = label(k, 'wsrc');  if (t) b.push(t);
    if (val(id, 'chiller') === 'yes') b.push('チラーあり');
    k.k = 'water_depth'; t = label(k, 'depth'); if (t) b.push(t);
    if (b.length) { out += step('水風呂', 'COLD BATH', b); steps++; }

    var c = [];
    if (val(id, 'outdoor_rest') === 'yes') c.push('外気浴スペースあり');
    k.k = 'rest_chair'; t = label(k, 'chair'); if (t && t !== 'なし') c.push(t);
    if (c.length) { out += step('外気浴', 'AIR BATH', c); steps++; }

    if (steps < 2) return '';
    return '<div class="flow-wrap">' + out + '</div>';
  }

  /* ---------------------------------------------------------------
     3. 似たサウナのヴィラ
     同じ県・同じ熱源・同じ形式・共通タグ・近い価格帯で点を付けて上位3件。
     **推薦のために新しい値を作らない。** 既存データの一致だけを見る。
  --------------------------------------------------------------- */
  function score(me, other) {
    var s = 0, i;
    if (me.p === other.p) s += 3;
    var a = val(me.i, 'stove'), b = val(other.i, 'stove');
    if (a && a === b) s += 3;
    a = val(me.i, 'sauna_type'); b = val(other.i, 'sauna_type');
    if (a && a === b) s += 2;
    a = val(me.i, 'loyly'); b = val(other.i, 'loyly');
    if (a === 'yes' && b === 'yes') s += 2;
    if (val(other.i, 'coldbath') && val(me.i, 'coldbath')) s += 1;
    for (i = 0; i < me.t.length; i++) {
      if (other.t.indexOf(me.t[i]) > -1) s += 1;
    }
    if (me.y && other.y && Math.abs(me.y - other.y) < 20000) s += 1;
    return s;
  }

  function reasons(me, other) {
    var r = [], k = { id: other.i, k: '' }, t;
    var a = val(me.i, 'stove'), b = val(other.i, 'stove');
    if (a && a === b) { k.k = 'stove'; t = label(k, 'stove'); if (t) r.push(t); }
    a = val(me.i, 'sauna_type'); b = val(other.i, 'sauna_type');
    if (a && a === b) { k.k = 'sauna_type'; t = label(k, 'saunatype'); if (t) r.push(t); }
    if (val(me.i, 'loyly') === 'yes' && val(other.i, 'loyly') === 'yes') r.push('セルフロウリュ');
    for (var i = 0; i < me.t.length && r.length < 4; i++) {
      if (other.t.indexOf(me.t[i]) > -1 && TAG_JP[me.t[i]] && me.t[i] !== 'sauna') {
        r.push(TAG_JP[me.t[i]]);
      }
    }
    if (me.p === other.p && PREF_JP[other.p]) r.push(PREF_JP[other.p]);
    return r.slice(0, 4);
  }

  function similarHTML(id) {
    var me = null, i;
    for (i = 0; i < LITE.length; i++) { if (LITE[i].i === id) { me = LITE[i]; break; } }
    if (!me) return '';
    if (!val(id, 'sauna_exists') || val(id, 'sauna_exists') === 'no') return '';

    var cand = [];
    for (i = 0; i < LITE.length; i++) {
      var o = LITE[i];
      if (o.i === id || !o.s) continue;
      var ex = val(o.i, 'sauna_exists');
      if (!ex || ex === 'no') continue;
      var sc = score(me, o);
      if (sc >= 5) cand.push({ v: o, s: sc });
    }
    if (cand.length < 2) return '';
    cand.sort(function (x, y) { return y.s - x.s; });

    var out = '<div class="sim-h"><b>似たサウナのヴィラ</b><span>SIMILAR SAUNA VILLAS</span></div><div class="sim-list">';
    for (i = 0; i < Math.min(3, cand.length); i++) {
      var v = cand[i].v, rs = reasons(me, v);
      out += '<a class="sim-i" href="' + esc(v.s) + '.html">' +
             '<span class="sim-pref">' + esc(PREF_JP[v.p] || '') + '</span>' +
             '<span class="sim-n">' + esc(v.n) + '</span>' +
             '<span class="sim-r">' + esc(rs.join(' · ')) + '</span>' +
             '<span class="sim-p">' + esc(v.pp || '') + '</span></a>';
    }
    return out + '</div>';
  }

  /* ---------------------------------------------------------------
     4. スマートフォンの固定CTA
     本文を隠さないよう、高さは 56px 前後に留める。押すと予約サイトの一覧へ。
  --------------------------------------------------------------- */
  function stickyCTA() {
    var ota = document.querySelector('.ota-grid');
    if (!ota) return;                       /* 予約サイトが無い施設には出さない */
    var priceEl = document.querySelector('.modal-price');
    var price = priceEl ? priceEl.textContent.replace(/\s+/g, ' ') : '';
    var bar = document.createElement('div');
    bar.className = 'sticky-cta';
    bar.innerHTML = '<span class="sticky-price">' + esc(price) + '</span>' +
                    '<button type="button" class="sticky-btn">空室・料金を見る</button>';
    document.body.appendChild(bar);
    bar.querySelector('.sticky-btn').onclick = function () {
      var lab = document.querySelector('.modal-ota-label') || ota;
      lab.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    /* 予約欄が見えている間は隠す（二重に出さない） */
    if (window.IntersectionObserver) {
      var io = new IntersectionObserver(function (es) {
        for (var i = 0; i < es.length; i++) {
          bar.className = es[i].isIntersecting ? 'sticky-cta is-off' : 'sticky-cta';
        }
      }, { rootMargin: '-40% 0px -20% 0px' });
      io.observe(ota);
    }
  }

  function mount(cls, html) {
    var els = document.getElementsByClassName(cls), i;
    for (i = 0; i < els.length; i++) {
      var id = parseInt(els[i].getAttribute('data-villa-id'), 10);
      var h = html(id);
      if (h) { els[i].innerHTML = h; } else { els[i].parentNode.removeChild(els[i]); i--; }
    }
  }

  function init() {
    mount('sauna-glance', glanceHTML);
    mount('sauna-flow', flowHTML);
    mount('similar-villas', similarHTML);
    stickyCTA();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, false);
  } else {
    init();
  }
})();
