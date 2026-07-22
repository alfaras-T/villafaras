/* ==========================================================================
   villafaras 一次データ（施設スペック）スキーマ + レンダラ
   --------------------------------------------------------------------------
   ・項目定義はこのファイル1箇所のみ。項目追加時に286件のHTMLを触る必要はない。
   ・値は VILLAFARAS_SPEC に villaId をキーとして格納する。
   ・未定義の項目は「未調査」として描画される（「なし」とは明確に区別する）。
   ・ES5構文のみ / XHR + onreadystatechange / 外部ライブラリ不使用（iPad Safari対応）
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     1. 出典（src）ラベル
        owner  = 施設回答（オーナー確認済み）
        desk   = 公式サイト調べ（要出典URL）
        auto   = 座標から自動算出
        review = 宿泊者レビューの集計
     ------------------------------------------------------------------ */
  var SRC = {
    owner:  { t: '施設', c: 'src-owner' },
    desk:   { t: '公式', c: 'src-desk' },
    auto:   { t: '自動', c: 'src-auto' },
    review: { t: '宿泊者', c: 'src-review' }
  };

  /* ------------------------------------------------------------------
     2. 選択肢マスタ
        ※ 数値項目は実数ではなく「階段」で持つ。回答のばらつきを吸収するため。
     ------------------------------------------------------------------ */
  var O = {
    yesno:    { yes: 'あり', no: 'なし' },
    kahi:     { yes: '可', no: '不可' },
    stove:    { wood: '薪ストーブ', electric: '電気ストーブ', gas: 'ガス' },
    saunatype:{ indoor: '室内サウナ', hut: 'サウナ小屋', barrel: 'バレルサウナ', tent: 'テントサウナ' },
    loyly:    { yes: 'セルフロウリュ可', auto: 'オートロウリュ', no: '不可' },
    heattime: { u30: '30分未満', m30: '30〜60分', m60: '60〜90分', o90: '90分以上', always: '常時稼働' },
    hours:    { h24: '24時間', limited: '時間制限あり', reserve: '要予約制' },
    coldbath: { bath: '水風呂', river: '川・湖', shower: 'シャワーのみ', none: 'なし' },
    wtemp:    { u10: '10℃未満', t1015: '10〜15℃', t1518: '15〜18℃', t1822: '18〜22℃', o22: '22℃以上' },
    wsrc:     { tap: '水道水', well: '井戸水・地下水', spring: '湧水', river: '川・湖' },
    depth:    { knee: '膝くらい', waist: '腰くらい', chest: '胸くらい', shoulder: '肩まで' },
    chair:    { infinity: 'インフィニティチェア', bench: 'ベンチ', chair: 'イス', none: 'なし' },
    villatype:{ solo: '完全独立一棟', multi: '複数棟サイト内', shared: '共用棟あり' },
    ndist:    { solo: '隣に建物なし', o50: '50m以上', u50: '50m未満', same: '同一建物内' },
    sound:    { free: '制限なし', night: '22時以降は配慮', noinst: '楽器・カラオケ不可' },
    ktype:    { ih: 'IH', gas: 'ガス', both: 'IH＋ガス', none: 'なし' },
    bbqroof:  { roof: '屋根あり（雨天可）', open: '屋根なし', none: 'BBQ不可' },
    cleanup:  { staff: '施設側', guest: '宿泊者' },
    firepit:  { stand: '焚き火台', direct: '直火可', no: '不可' },
    fee:      { incl: '料金に込み', extra: '別料金' },
    checkin:  { staff: '対面', smart: 'スマートロック', keybox: 'キーボックス' },
    late:     { ok: '可', contact: '要連絡', no: '不可' },
    bring:    { bring: '持参が必要', ready: '備品あり' },
    steps:    { flat: '平屋・段差なし', stairs: '階段あり' },
    winter:   { ok: '通年問題なし', snow: '積雪注意', tire: 'スタッドレス・チェーン推奨', closed: '冬季通行止めあり' },
    bugs:     { few: '気にならない', some: 'やや気になる', many: 'かなり気になる' },
    signal:   { good: '良好', weak: '弱い', none: '圏外' },
    noise:    { none: '気にならない', some: '少し聞こえる', much: '気になる' },
    comfort:  { ok: '定員通りで快適', tight: '定員だとやや窮屈' }
  };

  /* ------------------------------------------------------------------
     3. 項目スキーマ
        k    = フィールドキー（Firestore と共通）
        l    = 表示ラベル
        o    = 選択肢マスタ名（省略時は生値をそのまま表示）
        u    = 単位
        n    = ラベル下の補足（業界語の言い換えなど）
        ch   = 想定取得チャネル（owner / desk / auto / review）
     ------------------------------------------------------------------ */
  var SCHEMA = [
    { g: 'サウナ', rows: [
      { k: 'sauna_exists', l: 'サウナ',        o: 'yesno',     ch: 'desk' },
      { k: 'sauna_type',   l: '形式',          o: 'saunatype', ch: 'desk' },
      { k: 'stove',        l: '熱源',          o: 'stove',     ch: 'desk' },
      { k: 'sauna_temp',   l: '室温',          u: '℃',         ch: 'owner' },
      { k: 'sauna_cap',    l: 'サウナ定員',    u: '名',         ch: 'owner' },
      { k: 'loyly',        l: 'セルフロウリュ', o: 'loyly',     ch: 'owner', n: '石に水をかけられるか' },
      { k: 'heat_time',    l: '加温時間',      o: 'heattime',  ch: 'owner', n: '入れるようになるまで' },
      { k: 'sauna_hours',  l: '利用可能時間',  o: 'hours',     ch: 'owner' }
    ]},

    { g: '水風呂・外気浴', rows: [
      { k: 'coldbath',     l: '冷却設備',      o: 'coldbath',  ch: 'desk' },
      { k: 'chiller',      l: '水風呂チラー',  o: 'yesno',     ch: 'owner', n: '夏場も水温を保てる冷却装置' },
      { k: 'water_temp',   l: '夏場の水温',    o: 'wtemp',     ch: 'owner' },
      { k: 'water_src',    l: '水源',          o: 'wsrc',      ch: 'owner' },
      { k: 'water_depth',  l: '水深',          o: 'depth',     ch: 'owner' },
      { k: 'outdoor_rest', l: '外気浴スペース', o: 'yesno',     ch: 'desk' },
      { k: 'rest_chair',   l: '休憩イス',      o: 'chair',     ch: 'desk' }
    ]},

    { g: '貸切・音', rows: [
      { k: 'villa_type',    l: '貸切構成',     o: 'villatype', ch: 'desk' },
      { k: 'neighbor_dist', l: '隣棟との距離', o: 'ndist',     ch: 'owner' },
      { k: 'sound_rule',    l: '音のルール',   o: 'sound',     ch: 'owner' }
    ]},

    { g: 'キッチン・火まわり', rows: [
      { k: 'kitchen_type',    l: '加熱方式',     o: 'ktype',   ch: 'desk' },
      { k: 'kitchen_burners', l: 'コンロ口数',   u: '口',      ch: 'desk' },
      { k: 'bbq_roof',        l: 'BBQの屋根',    o: 'bbqroof', ch: 'desk', n: '雨天でもBBQできるか' },
      { k: 'bbq_cleanup',     l: 'BBQ後片付け',  o: 'cleanup', ch: 'owner' },
      { k: 'firepit',         l: '焚き火',       o: 'firepit', ch: 'desk' },
      { k: 'firewood_fee',    l: '薪代',         o: 'fee',     ch: 'owner' }
    ]},

    { g: '到着・チェックイン', rows: [
      { k: 'checkin_method', l: 'チェックイン方式', o: 'checkin', ch: 'owner' },
      { k: 'late_arrival',   l: '21時以降の到着',   o: 'late',    ch: 'owner' },
      { k: 'early_late',     l: 'アーリー / レイト', o: 'kahi',   ch: 'owner' }
    ]},

    { g: '追加料金', rows: [
      { k: 'fee_cleaning', l: '清掃費',       u: '円', ch: 'owner' },
      { k: 'fee_heating',  l: '暖房・光熱費', u: '円', ch: 'owner' },
      { k: 'fee_pet',      l: 'ペット同伴料', u: '円', ch: 'owner' },
      { k: 'fee_person',   l: '人数追加分',   u: '円/名', ch: 'owner' },
      { k: 'fee_bbq',      l: 'BBQ機材',      o: 'fee', ch: 'owner' }
    ]},

    { g: '持ち物', rows: [
      { k: 'bring_towel',     l: 'タオル',       o: 'bring', ch: 'owner' },
      { k: 'bring_amenity',   l: 'アメニティ',   o: 'bring', ch: 'owner' },
      { k: 'bring_seasoning', l: '調味料',       o: 'bring', ch: 'owner' },
      { k: 'bring_wrap',      l: 'ラップ・ホイル', o: 'bring', ch: 'owner' },
      { k: 'bring_trash',     l: 'ゴミ袋',       o: 'bring', ch: 'owner' }
    ]},

    { g: '同行者・設備', rows: [
      { k: 'capacity',     l: '定員',          u: '名', ch: 'desk' },
      { k: 'comfort_cap',  l: '推奨人数',      u: '名', ch: 'owner', n: 'ゆったり過ごせる人数' },
      { k: 'pet_ok',       l: 'ペット',        o: 'kahi', ch: 'desk' },
      { k: 'kids_free',    l: '添い寝無料',    u: '歳まで', ch: 'owner' },
      { k: 'steps',        l: '段差・階段',    o: 'steps', ch: 'desk' },
      { k: 'wifi',         l: 'Wi-Fi',         o: 'yesno', ch: 'desk' }
    ]},

    { g: 'アクセス・周辺', rows: [
      { k: 'winter_access', l: '冬季アクセス',   o: 'winter', ch: 'auto' },
      { k: 'elevation',     l: '標高',           u: 'm',   ch: 'auto' },
      { k: 'supermarket',   l: '最寄りスーパー', u: '分',  ch: 'auto', n: '車での所要時間' },
      { k: 'conveni',       l: '最寄りコンビニ', u: '分',  ch: 'auto' },
      { k: 'ic',            l: '最寄りIC',       u: '分',  ch: 'auto' },
      { k: 'station',       l: '最寄り駅',       u: '分',  ch: 'auto' },
      { k: 'onsen',         l: '最寄り日帰り温泉', u: '分', ch: 'auto' }
    ]},

    { g: '宿泊者レポート', rows: [
      { k: 'bugs',         l: '虫の多さ',       o: 'bugs',    ch: 'review' },
      { k: 'arrival_real', l: '実際の所要時間', u: '分',      ch: 'review' },
      { k: 'signal',       l: '携帯の電波',     o: 'signal',  ch: 'review' },
      { k: 'noise',        l: '隣棟の音',       o: 'noise',   ch: 'review' },
      { k: 'cap_comfort',  l: '定員での快適さ', o: 'comfort', ch: 'review' }
    ]}
  ];

  /* ------------------------------------------------------------------
     4. データ格納庫
        形式: VILLAFARAS_SPEC[villaId] = { fieldKey: {v:値, src:出典, at:調査日, url:出典URL} }
        ※ 値は簡略記法（文字列/数値のみ）でも可。その場合 src は未表示。
        ※ 現在は既存の5件のみ。残りは調査後にここへ追記する。
     ------------------------------------------------------------------ */
  var DATA = window.VILLAFARAS_SPEC || {};
  window.VILLAFARAS_SPEC = DATA;

  /* ------------------------------------------------------------------
     5. 描画
     ------------------------------------------------------------------ */
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function normalize(cell) {
    if (cell === undefined || cell === null || cell === '') return null;
    if (typeof cell === 'object') {
      if (cell.v === undefined || cell.v === null || cell.v === '') return null;
      return cell;
    }
    return { v: cell };
  }

  function renderValue(row, cell) {
    var raw = cell.v;
    var text;
    if (row.o && O[row.o] && O[row.o][raw] !== undefined) {
      text = O[row.o][raw];
    } else if (raw === true) {
      text = 'あり';
    } else if (raw === false) {
      text = 'なし';
    } else {
      text = String(raw) + (row.u ? row.u : '');
    }
    var cls = (raw === 'no' || raw === 'none' || raw === false) ? ' class="spec-no"' : '';
    var badge = '';
    if (cell.src && SRC[cell.src]) {
      badge = '<span class="spec-src ' + SRC[cell.src].c + '">' + SRC[cell.src].t + '</span>';
    }
    return '<span' + cls + '>' + esc(text) + '</span>' + badge;
  }

  function buildHTML(villaId) {
    var data = DATA[String(villaId)] || {};
    var total = 0, filled = 0;
    var groupsHTML = '';
    var i, j;

    for (i = 0; i < SCHEMA.length; i++) {
      var grp = SCHEMA[i];
      var rowsHTML = '';
      var gTotal = 0, gFilled = 0;

      for (j = 0; j < grp.rows.length; j++) {
        var row = grp.rows[j];
        var cell = normalize(data[row.k]);
        gTotal++; total++;
        if (cell) { gFilled++; filled++; }

        var label = '<span class="spec-k">' + esc(row.l) +
          (row.n ? '<small>' + esc(row.n) + '</small>' : '') + '</span>';
        var value = cell
          ? renderValue(row, cell)
          : '<span class="spec-none">未調査</span>';

        rowsHTML += '<div class="spec-row" data-k="' + esc(row.k) + '" data-filled="' +
          (cell ? '1' : '0') + '">' + label +
          '<span class="spec-v">' + value + '</span></div>';
      }

      groupsHTML +=
        '<div class="spec-group' + (gFilled > 0 ? ' is-open' : '') + '">' +
          '<div class="spec-group-head">' +
            '<span class="spec-group-name">' + esc(grp.g) + '</span>' +
            '<span class="spec-group-cnt">' + gFilled + ' / ' + gTotal + '</span>' +
            '<span class="spec-group-arw">▼</span>' +
          '</div>' +
          '<div class="spec-group-body">' + rowsHTML + '</div>' +
        '</div>';
    }

    var pct = total ? Math.round(filled / total * 100) : 0;

    return '' +
      '<div class="spec-head">' +
        '<span class="spec-title">施設スペック</span>' +
        '<span class="spec-cov">調査済み <b>' + filled + '</b> / ' + total + '</span>' +
      '</div>' +
      '<div class="spec-bar"><i style="width:' + pct + '%"></i></div>' +
      '<label class="spec-toggle"><input type="checkbox" class="spec-only-filled">調査済みの項目のみ表示</label>' +
      groupsHTML +
      '<div class="spec-foot">' +
        '出典 — ' +
        '<span class="spec-src src-owner">施設</span> 施設回答　' +
        '<span class="spec-src src-desk">公式</span> 公式サイト調べ　' +
        '<span class="spec-src src-auto">自動</span> 座標から算出　' +
        '<span class="spec-src src-review">宿泊者</span> レビュー集計<br>' +
        '「未調査」は情報が未確認であることを示すもので、設備が存在しないことを意味しません。' +
      '</div>' +
      '<a class="spec-owner-cta" href="' + (window.VILLAFARAS_SPEC_OWNER_URL || '../owner.html') + '">' +
        '施設関係者の方へ — 掲載情報を更新する' +
      '</a>';
  }

  /* --- イベント（委譲。個別バインドしないので再描画に強い） --- */
  function onClick(e) {
    var el = e.target;
    while (el && el !== document.body) {
      if (el.className && String(el.className).indexOf('spec-group-head') > -1) {
        var grp = el.parentNode;
        var open = String(grp.className).indexOf('is-open') > -1;
        grp.className = open ? 'spec-group' : 'spec-group is-open';
        return;
      }
      el = el.parentNode;
    }
  }

  function onChange(e) {
    var el = e.target;
    if (!el || !el.className || String(el.className).indexOf('spec-only-filled') < 0) return;
    var block = el;
    while (block && String(block.className || '').indexOf('spec-block') < 0) block = block.parentNode;
    if (!block) return;
    var rows = block.getElementsByClassName('spec-row');
    for (var i = 0; i < rows.length; i++) {
      var filled = rows[i].getAttribute('data-filled') === '1';
      rows[i].style.display = (el.checked && !filled) ? 'none' : '';
    }
    var groups = block.getElementsByClassName('spec-group');
    for (var g = 0; g < groups.length; g++) {
      var cnt = groups[g].getElementsByClassName('spec-group-cnt')[0];
      var has = cnt && cnt.innerHTML.indexOf('0 /') !== 0;
      groups[g].style.display = (el.checked && !has) ? 'none' : '';
    }
  }

  function render(container) {
    var villaId = container.getAttribute('data-villa-id');
    container.innerHTML = buildHTML(villaId);
  }

  function init() {
    var blocks = document.getElementsByClassName('spec-block');
    for (var i = 0; i < blocks.length; i++) render(blocks[i]);
    document.addEventListener('click', onClick, false);
    document.addEventListener('change', onChange, false);
  }

  /* index.html のモーダルからも同じ描画を使えるよう公開する */
  window.villafarasSpecHTML = buildHTML;
  window.villafarasSpecRender = render;
  window.VILLAFARAS_SPEC_SCHEMA = SCHEMA;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, false);
  } else {
    init();
  }
})();
