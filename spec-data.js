/* ==========================================================================
   villafaras 施設スペック データ
   --------------------------------------------------------------------------
   spec.js より先に読み込むこと。
   形式: VILLAFARAS_SPEC[villaId] = { fieldKey: { v: 値, src: 出典, at: 調査日, url: 出典URL } }

     src : 'owner'（施設回答） / 'desk'（公式サイト調べ） / 'auto'（座標算出） / 'review'（宿泊者）
     at  : 'YYYY-MM' 形式の調査日
     url : src が 'desk' の場合は出典URLを必ず記録する

   アクセス系（標高・最寄り各所）はチャネルAで自動導出したもの。
   座標は Google Places（施設名+住所）で取得し、既知の32件と照合して検証済み。
   周辺施設: OpenStreetMap contributors (ODbL) / 標高: 国土地理院
   所要時間: OSRM による車のルート計算（直線距離ではない）
   ========================================================================== */
window.VILLAFARAS_SPEC = {

  "0": {  /* 古民家宿るうふ 揺之家 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type: { v: 'ih', src: 'desk', at: '2026-07' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '君津PA(上り) スマートIC 9分', src: 'auto', at: '2026-07' },
    station:      { v: '大貫 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "1": {  /* 古民家宿るうふ 清之家 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    sauna_cap:    { v: 4, src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    kitchen_type: { v: 'gas', src: 'desk', at: '2026-07' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 43, src: 'auto', at: '2026-07' },
    supermarket:  { v: 15, src: 'auto', at: '2026-07' },
    conveni:      { v: 12, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 26分', src: 'auto', at: '2026-07' },
    station:      { v: '和田浦 13分', src: 'auto', at: '2026-07' },
    onsen:        { v: 12, src: 'auto', at: '2026-07' }
  },

  "2": {  /* 古民家宿るうふ 波之家 */
    sauna_exists: { v: 'no', src: 'desk', at: '2026-08', url: 'https://travel.rakuten.co.jp/HOTEL/183522/183522.html' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 26, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '市原鶴舞IC 32分', src: 'auto', at: '2026-07' },
    station:      { v: '浪花 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "3": {  /* 古民家宿るうふ 遊之家 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type: { v: 'gas', src: 'desk', at: '2026-07' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 16, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '千葉北IC 8分', src: 'auto', at: '2026-07' },
    station:      { v: '東葉勝田台 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "4": {  /* るうふ別邸 鴨川919 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type: { v: 'gas', src: 'desk', at: '2026-07' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 96, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南富山IC 21分', src: 'auto', at: '2026-07' },
    station:      { v: '安房鴨川 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' },
    fee_bbq:      { v: 'incl', src: 'desk', at: '2026-07' }
  },

  "5": {  /* ＆SUN Hung five */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 5, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南富山IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '岩井 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "6": {  /* CAP MARTIN Funny house */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 5, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南富山IC 6分', src: 'auto', at: '2026-07' },
    station:      { v: '岩井 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "7": {  /* PREMIUM Funny house */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 4, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '富津金谷IC 3分', src: 'auto', at: '2026-07' },
    station:      { v: '浜金谷 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "8": {  /* &SUN Laie back */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 5, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南富山IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '岩井 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "9": {  /* sendouQ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 1, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 5分', src: 'auto', at: '2026-07' },
    station:      { v: '上総一ノ宮 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "10": {  /* sendouQ second／sendouQ third dog */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 1, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 5分', src: 'auto', at: '2026-07' },
    station:      { v: '上総一ノ宮 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "11": {  /* Avalon Cove */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 19, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '東浪見 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 15, src: 'auto', at: '2026-07' }
  },

  "12": {  /* Villa Torami */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 4, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '東浪見 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "13": {  /* Ocean's Terrace TORAMII */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    sauna_temp:   { v: '80〜90', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 2, src: 'auto', at: '2026-07' },
    supermarket:  { v: 13, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 12分', src: 'auto', at: '2026-07' },
    station:      { v: '東浪見 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "14": {  /* Sea by TORAMII */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 10, src: 'auto', at: '2026-07' },
    supermarket:  { v: 11, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 12分', src: 'auto', at: '2026-07' },
    station:      { v: '東浪見 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 12, src: 'auto', at: '2026-07' }
  },

  "15": {  /* amane */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南保田IC 3分', src: 'auto', at: '2026-07' },
    station:      { v: '保田 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "16": {  /* みささ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.awa-misasa.com/spa/' },
    sauna_hours:  { v: 'limited', src: 'desk', at: '2026-08', url: 'https://www.awa-misasa.com/room/' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    water_src:    { v: 'spring', src: 'desk', at: '2026-08', url: 'https://www.awa-misasa.com/spa/' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.awa-misasa.com/spa/' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.awa-misasa.com/room/' },
    elevation:    { v: 2, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南富山IC 5分', src: 'auto', at: '2026-07' },
    station:      { v: '安房勝山 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "17": {  /* the MELLOW HOUSE 館山 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-08', url: 'https://www.mellowhouse.jp/question/' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.mellowhouse.jp/question/' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'no', src: 'desk', at: '2026-08', url: 'https://www.mellowhouse.jp/question/' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 10, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 21分', src: 'auto', at: '2026-07' },
    station:      { v: '館山 17分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' },
    early_late:   { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.mellowhouse.jp/question/' },
    fee_bbq:      { v: 'extra', src: 'desk', at: '2026-08', url: 'https://www.mellowhouse.jp/question/' }
  },

  "18": {  /* On the wave 館山 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    stove:           { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/?gallery=bath' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/?gallery=bath' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/?gallery=bath' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/qa/' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    steps:           { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/qa/' },
    elevation:       { v: 4, src: 'auto', at: '2026-07' },
    supermarket:     { v: 8, src: 'auto', at: '2026-07' },
    conveni:         { v: 10, src: 'auto', at: '2026-07' },
    ic:              { v: '富浦IC 21分', src: 'auto', at: '2026-07' },
    station:         { v: '館山 17分', src: 'auto', at: '2026-07' },
    onsen:           { v: 7, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/?gallery=bath' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/qa/' },
    checkin_method:  { v: 'keybox', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/qa/' },
    early_late:      { v: 'yes', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/qa/' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://otw-tateyama.com/qa/' }
  },

  "19": {  /* GIFTHOUSE 館山 那古海岸 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'indoor', src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/activity.php' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/room.php' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/room.php' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    elevation:       { v: 2, src: 'auto', at: '2026-07' },
    supermarket:     { v: 2, src: 'auto', at: '2026-07' },
    conveni:         { v: 1, src: 'auto', at: '2026-07' },
    ic:              { v: '富浦IC 4分', src: 'auto', at: '2026-07' },
    station:         { v: '那古船形 2分', src: 'auto', at: '2026-07' },
    onsen:           { v: 5, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/room.php' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/activity.php' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/activity.php' },
    late_arrival:    { v: 'no', src: 'desk', at: '2026-08', url: 'https://nagokaigan.gifthouse.jp/nagokaigan/' }
  },

  "20": {  /* GIFTHOUSE 2nd 館山 洲宮 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'barrel', src: 'desk', at: '2026-07' },
    stove:           { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/activity.php' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/activity.php' },
    rest_chair:      { v: 'chair', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/activity.php' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/' },
    kitchen_type:    { v: 'gas', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/room.php' },
    kitchen_burners: { v: 1, src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/room.php' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 13, src: 'auto', at: '2026-07' },
    supermarket:     { v: 6, src: 'auto', at: '2026-07' },
    conveni:         { v: 6, src: 'auto', at: '2026-07' },
    ic:              { v: '富浦IC 16分', src: 'auto', at: '2026-07' },
    station:         { v: '館山 13分', src: 'auto', at: '2026-07' },
    onsen:           { v: 5, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/room.php' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/room.php' },
    late_arrival:    { v: 'ok', src: 'desk', at: '2026-08', url: 'https://gifthouse.jp/sunomiya/room.php' }
  },

  "21": {  /* UMInoTERRACE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 3, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 20分', src: 'auto', at: '2026-07' },
    station:      { v: '千倉 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 16, src: 'auto', at: '2026-07' }
  },

  "22": {  /* 海都-kaito- TOKYOBAY */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'indoor', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    rest_chair:      { v: 'chair', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    kitchen_type:    { v: 'gas', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    capacity:        { v: 9, src: 'desk', at: '2026-07' },
    elevation:       { v: 10, src: 'auto', at: '2026-07' },
    supermarket:     { v: 6, src: 'auto', at: '2026-07' },
    conveni:         { v: 1, src: 'auto', at: '2026-07' },
    ic:              { v: '富津金谷IC 2分', src: 'auto', at: '2026-07' },
    station:         { v: '浜金谷 1分', src: 'auto', at: '2026-07' },
    onsen:           { v: 1, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/faq' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://piyoresort.com/kaito/room' }
  },

  "23": {  /* The TRAVELERS Chateau Tateyama */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 62, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 5分', src: 'auto', at: '2026-07' },
    station:      { v: '富浦 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "24": {  /* BEST SPA 99 */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:    { v: 'barrel', src: 'desk', at: '2026-07' },
    sauna_temp:    { v: 100, src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    sauna_cap:     { v: 3, src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    sauna_hours:   { v: 'limited', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    firepit:       { v: 'no', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    capacity:      { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    steps:         { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    elevation:     { v: 2, src: 'auto', at: '2026-07' },
    supermarket:   { v: 5, src: 'auto', at: '2026-07' },
    conveni:       { v: 1, src: 'auto', at: '2026-07' },
    ic:            { v: '真亀JCT 4分', src: 'auto', at: '2026-07' },
    station:       { v: '東金 12分', src: 'auto', at: '2026-07' },
    onsen:         { v: 10, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' },
    fee_bbq:       { v: 'incl', src: 'desk', at: '2026-08', url: 'https://bestspa99.com/' }
  },

  "25": {  /* THE POOL HOUSE TOKYO BAY */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 4, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '谷津船橋 IC 2分', src: 'auto', at: '2026-07' },
    station:      { v: '南船橋 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "26": {  /* THE POOL HOUSE 木更津 */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.chillnn.com/ja/19a7b2c445a3bb' },
    capacity:      { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'no', src: 'desk', at: '2026-08', url: 'https://www.chillnn.com/ja/19a7b2c445a3bb' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.chillnn.com/ja/19a7b2c445a3bb' },
    elevation:     { v: 2, src: 'auto', at: '2026-07' },
    supermarket:   { v: 4, src: 'auto', at: '2026-07' },
    conveni:       { v: 3, src: 'auto', at: '2026-07' },
    ic:            { v: '袖ヶ浦 7分', src: 'auto', at: '2026-07' },
    station:       { v: '袖ケ浦 4分', src: 'auto', at: '2026-07' },
    onsen:         { v: 4, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.chillnn.com/ja/19a7b2c445a3bb' },
    fee_bbq:       { v: 'extra', src: 'desk', at: '2026-08', url: 'https://www.chillnn.com/ja/19a7b2c445a3bb' },
    late_arrival:  { v: 'contact', src: 'desk', at: '2026-08', url: 'https://www.chillnn.com/ja/19a7b2c445a3bb' }
  },

  "27": {  /* Sumera Resort Minato */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:      { v: 'bath', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' },
    villa_type:    { v: 'multi', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' },
    firepit:       { v: 'stand', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' },
    capacity:      { v: 3, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    steps:         { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' },
    elevation:     { v: 3, src: 'auto', at: '2026-07' },
    supermarket:   { v: 7, src: 'auto', at: '2026-07' },
    conveni:       { v: 3, src: 'auto', at: '2026-07' },
    ic:            { v: '富津中央IC 12分', src: 'auto', at: '2026-07' },
    station:       { v: '上総湊 4分', src: 'auto', at: '2026-07' },
    onsen:         { v: 7, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' },
    firewood_fee:  { v: 'incl', src: 'desk', at: '2026-08', url: 'https://sumera.co.jp/minato/' }
  },

  "28": {  /* VACATIONHOUSE TORAMI 7521 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 7, src: 'auto', at: '2026-07' },
    supermarket:  { v: 12, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '東浪見 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 12, src: 'auto', at: '2026-07' }
  },

  "29": {  /* PRIVE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-08', url: 'https://sauna-ikitai.com/saunas/87598' },
    stove:        { v: 'electric', src: 'desk', at: '2026-08', url: 'https://sauna-ikitai.com/saunas/87598' },
    sauna_temp:   { v: 100, src: 'desk', at: '2026-08', url: 'https://sauna-ikitai.com/saunas/87598' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://travel.yahoo.co.jp/00051452/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '八積 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' },
    late_arrival: { v: 'no', src: 'desk', at: '2026-08', url: 'https://travel.yahoo.co.jp/00051452/' }
  },

  "30": {  /* STRADDIE HOUSE */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'indoor', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    stove:           { v: 'electric', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    rest_chair:      { v: 'chair', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    kitchen_type:    { v: 'gas', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    steps:           { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    elevation:       { v: 16, src: 'auto', at: '2026-07' },
    supermarket:     { v: 11, src: 'auto', at: '2026-07' },
    conveni:         { v: 7, src: 'auto', at: '2026-07' },
    ic:              { v: '富浦IC 18分', src: 'auto', at: '2026-07' },
    station:         { v: '館山 13分', src: 'auto', at: '2026-07' },
    onsen:           { v: 10, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://straddiehouse.com/tateyama/' }
  },

  "31": {  /* moe-luana */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:    { v: 'barrel', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-luana' },
    loyly:         { v: 'yes', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-luana' },
    outdoor_rest:  { v: 'yes', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-luana' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-luana' },
    bbq_roof:      { v: 'roof', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-luana' },
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:     { v: 2, src: 'auto', at: '2026-07' },
    supermarket:   { v: 8, src: 'auto', at: '2026-07' },
    conveni:       { v: 1, src: 'auto', at: '2026-07' },
    ic:            { v: '長生IC 7分', src: 'auto', at: '2026-07' },
    station:       { v: '上総一ノ宮 3分', src: 'auto', at: '2026-07' },
    onsen:         { v: 7, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-luana' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-luana' }
  },

  "32": {  /* moe-akala,moe-aina */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:    { v: 'barrel', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    sauna_cap:     { v: 8, src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    loyly:         { v: 'yes', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    coldbath:      { v: 'bath', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    outdoor_rest:  { v: 'yes', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    bbq_roof:      { v: 'roof', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:     { v: 2, src: 'auto', at: '2026-07' },
    supermarket:   { v: 5, src: 'auto', at: '2026-07' },
    conveni:       { v: 1, src: 'auto', at: '2026-07' },
    ic:            { v: '長生IC 1分', src: 'auto', at: '2026-07' },
    station:       { v: '上総一ノ宮 7分', src: 'auto', at: '2026-07' },
    onsen:         { v: 1, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://moe-resort.co.jp/moe-akala-moe-aina' }
  },

  "33": {  /* and RIVER勝浦 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' },
    elevation:       { v: 48, src: 'auto', at: '2026-07' },
    supermarket:     { v: 9, src: 'auto', at: '2026-07' },
    conveni:         { v: 3, src: 'auto', at: '2026-07' },
    ic:              { v: '市原鶴舞IC 17分', src: 'auto', at: '2026-07' },
    station:         { v: '総元 3分', src: 'auto', at: '2026-07' },
    onsen:           { v: 9, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' },
    checkin_method:  { v: 'smart', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' },
    early_late:      { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://www.andriver-katsuura.com/' }
  },

  "34": {  /* Retreat Villa Aym */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'indoor', src: 'desk', at: '2026-07' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    sauna_hours:     { v: 'limited', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    rest_chair:      { v: 'chair', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    villa_type:      { v: 'multi', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    capacity:        { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'no', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    elevation:       { v: 12, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 4, src: 'auto', at: '2026-07' },
    ic:              { v: '富浦IC 17分', src: 'auto', at: '2026-07' },
    station:         { v: '館山 14分', src: 'auto', at: '2026-07' },
    onsen:           { v: 6, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    early_late:      { v: 'yes', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' },
    late_arrival:    { v: 'no', src: 'desk', at: '2026-08', url: 'https://aym.wyes-resort.com/' }
  },

  "35": {  /* by the river Isumi */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 7, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 17分', src: 'auto', at: '2026-07' },
    station:      { v: '太東 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 17, src: 'auto', at: '2026-07' }
  },

  "36": {  /* STAR VILLAGE TATEYAMA */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.star-village.net/rooms' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://www.star-village.net/rooms' },
    firepit:         { v: 'stand', src: 'desk', at: '2026-08', url: 'https://www.star-village.net/rooms' },
    capacity:        { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 33, src: 'auto', at: '2026-07' },
    supermarket:     { v: 4, src: 'auto', at: '2026-07' },
    conveni:         { v: 2, src: 'auto', at: '2026-07' },
    ic:              { v: '富浦IC 10分', src: 'auto', at: '2026-07' },
    station:         { v: '館山 5分', src: 'auto', at: '2026-07' },
    onsen:           { v: 6, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.star-village.net/rooms' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.star-village.net/rooms' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.star-village.net/rooms' }
  },

  "37": {  /* VILLA SENSE kujukuri */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:    { v: 'barrel', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    stove:         { v: 'wood', src: 'desk', at: '2026-07' },
    sauna_cap:     { v: 6, src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    loyly:         { v: 'yes', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    sauna_hours:   { v: 'limited', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    coldbath:      { v: 'bath', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    bbq_roof:      { v: 'roof', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    firepit:       { v: 'stand', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    elevation:     { v: 2, src: 'auto', at: '2026-07' },
    supermarket:   { v: 2, src: 'auto', at: '2026-07' },
    conveni:       { v: 1, src: 'auto', at: '2026-07' },
    ic:            { v: '片貝IC 2分', src: 'auto', at: '2026-07' },
    station:       { v: '東金 11分', src: 'auto', at: '2026-07' },
    onsen:         { v: 13, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://villa-sense-kujukuri.com/' }
  },

  "38": {  /* Asile＆OLILI */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'barrel', src: 'desk', at: '2026-07' },
    stove:           { v: 'electric', src: 'desk', at: '2026-08', url: 'https://asile-villa.com/' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://asile-villa.com/' },
    sauna_hours:     { v: 'limited', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    villa_type:      { v: 'multi', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    firepit:         { v: 'no', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    capacity:        { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'no', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    elevation:       { v: 30, src: 'auto', at: '2026-07' },
    supermarket:     { v: 7, src: 'auto', at: '2026-07' },
    conveni:         { v: 3, src: 'auto', at: '2026-07' },
    ic:              { v: '富津金谷IC 4分', src: 'auto', at: '2026-07' },
    station:         { v: '竹岡 2分', src: 'auto', at: '2026-07' },
    onsen:           { v: 1, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://olili.asile-villa.com/' }
  },

  "39": {  /* VILLA UMICHIKA 九十九里一宮 */
    sauna_exists:   { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:     { v: 'barrel', src: 'desk', at: '2026-07' },
    loyly:          { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_hours:    { v: 'limited', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    outdoor_rest:   { v: 'yes', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    villa_type:     { v: 'multi', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    kitchen_type:   { v: 'ih', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    bbq_roof:       { v: 'roof', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    capacity:       { v: 8, src: 'desk', at: '2026-07' },
    elevation:      { v: 3, src: 'auto', at: '2026-07' },
    supermarket:    { v: 12, src: 'auto', at: '2026-07' },
    conveni:        { v: 4, src: 'auto', at: '2026-07' },
    ic:             { v: '長生IC 11分', src: 'auto', at: '2026-07' },
    station:        { v: '東浪見 4分', src: 'auto', at: '2026-07' },
    onsen:          { v: 10, src: 'auto', at: '2026-07' },
    bring_amenity:  { v: 'ready', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    bring_towel:    { v: 'ready', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    checkin_method: { v: 'keybox', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' },
    fee_bbq:        { v: 'extra', src: 'desk', at: '2026-08', url: 'https://umichika.jp/villa/' }
  },

  "40": {  /* THE BLUE POINT seaside villa */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://aonoie.jp/bluepoint/facilities.html' },
    kitchen_type:    { v: 'gas', src: 'desk', at: '2026-08', url: 'https://aonoie.jp/bluepoint/facilities.html' },
    capacity:        { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://aonoie.jp/bluepoint/facilities.html' },
    elevation:       { v: 4, src: 'auto', at: '2026-07' },
    supermarket:     { v: 12, src: 'auto', at: '2026-07' },
    conveni:         { v: 3, src: 'auto', at: '2026-07' },
    ic:              { v: '長生IC 10分', src: 'auto', at: '2026-07' },
    station:         { v: '東浪見 4分', src: 'auto', at: '2026-07' },
    onsen:           { v: 9, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://aonoie.jp/bluepoint/facilities.html' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://aonoie.jp/bluepoint/facilities.html' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://aonoie.jp/bluepoint/facilities.html' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://aonoie.jp/bluepoint/facilities.html' }
  },

  "41": {  /* ビーチテラス房総 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'indoor', src: 'desk', at: '2026-08', url: 'https://beach-terrace.jp/boso/' },
    sauna_cap:    { v: 3, src: 'desk', at: '2026-08', url: 'https://beach-terrace.jp/boso/' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-08', url: 'https://beach-terrace.jp/boso/' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    steps:        { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://beach-terrace.jp/boso/' },
    elevation:    { v: 7, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '富津金谷IC 4分', src: 'auto', at: '2026-07' },
    station:      { v: '浜金谷 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "42": {  /* 雫花 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 2, src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '館山 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "43": {  /* Montevan RESORT VILLA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 8, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 12分', src: 'auto', at: '2026-07' },
    station:      { v: '館山 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "44": {  /* 久留里山荘（QULRI SANSO） */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 55, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '木更津東IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '小櫃 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 13, src: 'auto', at: '2026-07' }
  },

  "45": {  /* HARUKA KANATA 森のヴィラ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-08', url: 'https://harukakanata2.heteml.net/' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    sauna_temp:   { v: 105, src: 'desk', at: '2026-08', url: 'https://sauna-ikitai.com/saunas/78941' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-08', url: 'https://harukakanata2.heteml.net/' },
    sauna_hours:  { v: 'limited', src: 'desk', at: '2026-08', url: 'https://sauna-ikitai.com/saunas/78941' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-08', url: 'https://harukakanata2.heteml.net/' },
    water_temp:   { v: 't1518', src: 'desk', at: '2026-08', url: 'https://sauna-ikitai.com/saunas/78941' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-08', url: 'https://harukakanata2.heteml.net/' },
    villa_type:   { v: 'multi', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00051622/' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-08', url: 'https://harukakanata2.heteml.net/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 70, src: 'auto', at: '2026-07' },
    supermarket:  { v: 12, src: 'auto', at: '2026-07' },
    conveni:      { v: 10, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南富山IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '岩井 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 14, src: 'auto', at: '2026-07' },
    late_arrival: { v: 'no', src: 'desk', at: '2026-08', url: 'https://travel.rakuten.co.jp/HOTEL/186100/186100.html' }
  },

  "46": {  /* 閑閑舎 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://kankansha.com/equipment/' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    rest_chair:      { v: 'chair', src: 'desk', at: '2026-08', url: 'https://kankansha.com/equipment/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://kankansha.com/equipment/' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    elevation:       { v: 2, src: 'auto', at: '2026-07' },
    supermarket:     { v: 4, src: 'auto', at: '2026-07' },
    conveni:         { v: 4, src: 'auto', at: '2026-07' },
    ic:              { v: '片貝IC 6分', src: 'auto', at: '2026-07' },
    station:         { v: '求名 12分', src: 'auto', at: '2026-07' },
    onsen:           { v: 19, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://kankansha.com/equipment/' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://kankansha.com/equipment/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://kankansha.com/equipment/' },
    firewood_fee:    { v: 'incl', src: 'desk', at: '2026-08', url: 'https://kankansha.com/equipment/' }
  },

  "47": {  /* Hackberry Holiday Home */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    elevation:    { v: 38, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '下総IC 14分', src: 'auto', at: '2026-07' },
    station:      { v: '滑河 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 15, src: 'auto', at: '2026-07' }
  },

  "48": {  /* 庄屋の里 古民家たなか */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 12, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '太東 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 15, src: 'auto', at: '2026-07' }
  },

  "49": {  /* 古民家一棟貸切旅館　成田さくら邸 */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://www.okamura-is.co.jp/kaguyanomori/' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 26, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '佐倉IC 9分', src: 'auto', at: '2026-07' },
    station:      { v: '京成臼井 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "50": {  /* THE CLUB 919 DOG FRIENDLY */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:         { v: 'yes', src: 'desk', at: '2026-08', url: 'https://theclub919.com/facilities/' },
    kitchen_type:  { v: 'ih', src: 'desk', at: '2026-08', url: 'https://theclub919.com/facilities/' },
    capacity:      { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://theclub919.com/facilities/' },
    elevation:     { v: 2, src: 'auto', at: '2026-07' },
    supermarket:   { v: 3, src: 'auto', at: '2026-07' },
    conveni:       { v: 1, src: 'auto', at: '2026-07' },
    ic:            { v: '真亀JCT 2分', src: 'auto', at: '2026-07' },
    station:       { v: '東金 10分', src: 'auto', at: '2026-07' },
    onsen:         { v: 11, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://theclub919.com/facilities/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://theclub919.com/facilities/' }
  },

  "51": {  /* 九十九里 point59 */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://bai-bain.com/property/017_Point59.html' },
    kitchen_type:  { v: 'ih', src: 'desk', at: '2026-08', url: 'https://bai-bain.com/property/017_Point59.html' },
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    steps:         { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://bai-bain.com/property/017_Point59.html' },
    elevation:     { v: 2, src: 'auto', at: '2026-07' },
    supermarket:   { v: 3, src: 'auto', at: '2026-07' },
    conveni:       { v: 1, src: 'auto', at: '2026-07' },
    ic:            { v: '真亀JCT 2分', src: 'auto', at: '2026-07' },
    station:       { v: '東金 10分', src: 'auto', at: '2026-07' },
    onsen:         { v: 11, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://bai-bain.com/property/017_Point59.html' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://bai-bain.com/property/017_Point59.html' }
  },

  "52": {  /* 緑邸～OHTAKI～ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 22, src: 'auto', at: '2026-07' },
    supermarket:  { v: 12, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '市原鶴舞IC 14分', src: 'auto', at: '2026-07' },
    station:      { v: '上総中川 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 17, src: 'auto', at: '2026-07' }
  },

  "53": {  /* tokoro hotel Isumi */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    elevation:    { v: 14, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '茂原長南IC 26分', src: 'auto', at: '2026-07' },
    station:      { v: '新田野 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 15, src: 'auto', at: '2026-07' }
  },

  "54": {  /* Zekkei stay ISUMI cabin */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 4, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 18分', src: 'auto', at: '2026-07' },
    station:      { v: '太東 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 18, src: 'auto', at: '2026-07' }
  },

  "55": {  /* SEA-LIFE TSURIGASAKI */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:    { v: 'barrel', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' },
    stove:         { v: 'gas', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' },
    loyly:         { v: 'yes', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' },
    coldbath:      { v: 'bath', src: 'desk', at: '2026-07' },
    water_src:     { v: 'well', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' },
    outdoor_rest:  { v: 'yes', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' },
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:     { v: 5, src: 'auto', at: '2026-07' },
    supermarket:   { v: 12, src: 'auto', at: '2026-07' },
    conveni:       { v: 2, src: 'auto', at: '2026-07' },
    ic:            { v: '長生IC 13分', src: 'auto', at: '2026-07' },
    station:       { v: '東浪見 3分', src: 'auto', at: '2026-07' },
    onsen:         { v: 12, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://sea-life.ne.jp/accommodation/' }
  },

  "56": {  /* THE VIBES VILLA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-08', url: 'https://thevibesvilla.com/katsuura/plan/private-sauna/' },
    sauna_temp:   { v: 110, src: 'desk', at: '2026-08', url: 'https://thevibesvilla.com/katsuura/plan/private-sauna/' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-08', url: 'https://thevibesvilla.com/katsuura/plan/private-sauna/' },
    sauna_hours:  { v: 'limited', src: 'desk', at: '2026-08', url: 'https://thevibesvilla.com/katsuura/plan/private-sauna/' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-08', url: 'https://thevibesvilla.com/katsuura/plan/private-sauna/' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-08', url: 'https://thevibesvilla.com/katsuura/plan/private-sauna/' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://thevibesvilla.com/katsuura/' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 5, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '市原鶴舞IC 32分', src: 'auto', at: '2026-07' },
    station:      { v: '鵜原 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "57": {  /* Refwind */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://refwind.jp/' },
    bbq_roof:        { v: 'roof', src: 'desk', at: '2026-08', url: 'https://refwind.jp/' },
    firepit:         { v: 'stand', src: 'desk', at: '2026-08', url: 'https://refwind.jp/' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 24, src: 'auto', at: '2026-07' },
    supermarket:     { v: 3, src: 'auto', at: '2026-07' },
    conveni:         { v: 2, src: 'auto', at: '2026-07' },
    ic:              { v: '鋸南保田IC 2分', src: 'auto', at: '2026-07' },
    station:         { v: '保田 2分', src: 'auto', at: '2026-07' },
    onsen:           { v: 1, src: 'auto', at: '2026-07' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://refwind.jp/' }
  },

  "58": {  /* UMIYAMA CHIKURA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 30, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 17分', src: 'auto', at: '2026-07' },
    station:      { v: '千倉 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 13, src: 'auto', at: '2026-07' }
  },

  "59": {  /* Under the Sea UBARA */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:      { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:     { v: 6, src: 'auto', at: '2026-07' },
    supermarket:   { v: 9, src: 'auto', at: '2026-07' },
    conveni:       { v: 3, src: 'auto', at: '2026-07' },
    ic:            { v: '市原鶴舞IC 31分', src: 'auto', at: '2026-07' },
    station:       { v: '鵜原 2分', src: 'auto', at: '2026-07' },
    onsen:         { v: 9, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://undertheseaubara.snack.chillnn.com/ja' },
    kids_free:     { v: 5, src: 'desk', at: '2026-08', url: 'https://undertheseaubara.snack.chillnn.com/ja' },
    late_arrival:  { v: 'no', src: 'desk', at: '2026-08', url: 'https://undertheseaubara.snack.chillnn.com/ja' }
  },

  "60": {  /* and FOREST勝浦 竹の離れ */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    stove:           { v: 'electric', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    elevation:       { v: 73, src: 'auto', at: '2026-07' },
    supermarket:     { v: 8, src: 'auto', at: '2026-07' },
    conveni:         { v: 2, src: 'auto', at: '2026-07' },
    ic:              { v: '市原鶴舞IC 17分', src: 'auto', at: '2026-07' },
    station:         { v: '久我原 2分', src: 'auto', at: '2026-07' },
    onsen:           { v: 9, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    checkin_method:  { v: 'smart', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    early_late:      { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://www.takenohanare.com/' }
  },

  "61": {  /* 天神郷 昊 -Sora- */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    elevation:    { v: 61, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 8, src: 'auto', at: '2026-07' },
    ic:           { v: '鋸南富山IC 9分', src: 'auto', at: '2026-07' },
    station:      { v: '岩井 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "62": {  /* RICKA KATSUURA */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'hut', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    chiller:         { v: 'yes', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/' },
    villa_type:      { v: 'multi', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    firepit:         { v: 'stand', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    capacity:        { v: 9, src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    elevation:       { v: 80, src: 'auto', at: '2026-07' },
    supermarket:     { v: 10, src: 'auto', at: '2026-07' },
    conveni:         { v: 9, src: 'auto', at: '2026-07' },
    ic:              { v: '市原鶴舞IC 24分', src: 'auto', at: '2026-07' },
    station:         { v: '勝浦 10分', src: 'auto', at: '2026-07' },
    onsen:           { v: 10, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    firewood_fee:    { v: 'extra', src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/room/' },
    kids_free:       { v: 5, src: 'desk', at: '2026-08', url: 'https://ricka-resort.com/katsuura/' }
  },

  "63": {  /* Dear Wan Spa Garden */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 105, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '桂IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '本納 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "64": {  /* VILLA Seamu */
    sauna_exists:   { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:     { v: 'barrel', src: 'desk', at: '2026-07' },
    stove:          { v: 'electric', src: 'desk', at: '2026-08', url: 'https://www.aco.co.jp/1-theme-sauna/region-chiba.html' },
    sauna_cap:      { v: 4, src: 'desk', at: '2026-08', url: 'https://www.aco.co.jp/1-theme-sauna/region-chiba.html' },
    loyly:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.aco.co.jp/1-theme-sauna/region-chiba.html' },
    villa_type:     { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052182/11614497/10286630/' },
    firepit:        { v: 'stand', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052182/11614497/10286630/' },
    capacity:       { v: 11, src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052182/11614497/10286630/' },
    pet_ok:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:      { v: 3, src: 'auto', at: '2026-07' },
    supermarket:    { v: 4, src: 'auto', at: '2026-07' },
    conveni:        { v: 3, src: 'auto', at: '2026-07' },
    ic:             { v: '真亀JCT 5分', src: 'auto', at: '2026-07' },
    station:        { v: '東金 11分', src: 'auto', at: '2026-07' },
    onsen:          { v: 14, src: 'auto', at: '2026-07' },
    checkin_method: { v: 'keybox', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052182/11614497/10286630/' },
    late_arrival:   { v: 'ok', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052182/11614497/10286630/' }
  },

  "65": {  /* THE NALU */
    sauna_exists:   { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:     { v: 'solo', src: 'desk', at: '2026-08', url: 'https://the-nalu.com/information/' },
    capacity:       { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:      { v: 3, src: 'auto', at: '2026-07' },
    supermarket:    { v: 13, src: 'auto', at: '2026-07' },
    conveni:        { v: 4, src: 'auto', at: '2026-07' },
    ic:             { v: '長生IC 11分', src: 'auto', at: '2026-07' },
    station:        { v: '東浪見 4分', src: 'auto', at: '2026-07' },
    onsen:          { v: 11, src: 'auto', at: '2026-07' },
    bring_amenity:  { v: 'ready', src: 'desk', at: '2026-08', url: 'https://the-nalu.com/information/' },
    checkin_method: { v: 'smart', src: 'desk', at: '2026-08', url: 'https://the-nalu.com/information/' },
    early_late:     { v: 'yes', src: 'desk', at: '2026-08', url: 'https://the-nalu.com/information/' }
  },

  "66": {  /* Villa Yno */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 7, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富浦IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '館山 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "67": {  /* EKVOLI MARINA VILLA, Isumi Garden */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.ekvoli.com/ekvoli-marina-villa' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-08', url: 'https://www.ekvoli.com/ekvoli-marina-villa' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 3, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '長生IC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '長者町 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 19, src: 'auto', at: '2026-07' }
  },

  "68": {  /* SURF UP */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:    { v: 'solo', src: 'desk', at: '2026-08', url: 'https://surf-up.co.jp/' },
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    steps:         { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://surf-up.co.jp/' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://surf-up.co.jp/' },
    elevation:     { v: 4, src: 'auto', at: '2026-07' },
    supermarket:   { v: 10, src: 'auto', at: '2026-07' },
    conveni:       { v: 2, src: 'auto', at: '2026-07' },
    ic:            { v: '長生IC 9分', src: 'auto', at: '2026-07' },
    station:       { v: '東浪見 4分', src: 'auto', at: '2026-07' },
    onsen:         { v: 9, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://surf-up.co.jp/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://surf-up.co.jp/' }
  },

  "69": {  /* primera villa */
    capacity:    { v: 12, src: 'desk', at: '2026-08', url: 'https://www.primera-gr.co.jp/' },
    elevation:   { v: 23, src: 'auto', at: '2026-07' },
    supermarket: { v: 8, src: 'auto', at: '2026-07' },
    conveni:     { v: 3, src: 'auto', at: '2026-07' },
    ic:          { v: '富津金谷IC 4分', src: 'auto', at: '2026-07' },
    station:     { v: '竹岡 3分', src: 'auto', at: '2026-07' },
    onsen:       { v: 2, src: 'auto', at: '2026-07' }
  },

  "70": {  /* The Pacific Retreat TATEYAMA */
    sauna_exists:   { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/sauna%ef%bc%86bath-2/' },
    coldbath:       { v: 'bath', src: 'desk', at: '2026-07' },
    chiller:        { v: 'yes', src: 'desk', at: '2026-07' },
    water_temp:     { v: 't1518', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/sauna%ef%bc%86bath-2/' },
    outdoor_rest:   { v: 'yes', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/sauna%ef%bc%86bath-2/' },
    rest_chair:     { v: 'infinity', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/sauna%ef%bc%86bath-2/' },
    villa_type:     { v: 'solo', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/' },
    kitchen_type:   { v: 'ih', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/faq/' },
    capacity:       { v: 7, src: 'desk', at: '2026-07' },
    pet_ok:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:      { v: 26, src: 'auto', at: '2026-07' },
    supermarket:    { v: 6, src: 'auto', at: '2026-07' },
    conveni:        { v: 6, src: 'auto', at: '2026-07' },
    ic:             { v: '富浦IC 17分', src: 'auto', at: '2026-07' },
    station:        { v: '館山 14分', src: 'auto', at: '2026-07' },
    onsen:          { v: 4, src: 'auto', at: '2026-07' },
    checkin_method: { v: 'smart', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/faq/' },
    fee_bbq:        { v: 'incl', src: 'desk', at: '2026-08', url: 'https://pacific-retreat-tateyama.com/faq/' }
  },

  "71": {  /* Casita Laguna */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://www.casitalaguna.com/faq/' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.casitalaguna.com/about/' },
    capacity:        { v: 7, src: 'desk', at: '2026-07' },
    elevation:       { v: 3, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 2, src: 'auto', at: '2026-07' },
    ic:              { v: '長生IC 21分', src: 'auto', at: '2026-07' },
    station:         { v: '長者町 3分', src: 'auto', at: '2026-07' },
    onsen:           { v: 21, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.casitalaguna.com/faq/' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.casitalaguna.com/faq/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.casitalaguna.com/faq/' },
    fee_bbq:         { v: 'incl', src: 'desk', at: '2026-08', url: 'https://www.casitalaguna.com/faq/' }
  },

  "72": {  /* VILLA LAGI */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_temp:      { v: 65, src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    loyly:           { v: 'auto', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    sauna_hours:     { v: 'h24', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    water_src:       { v: 'well', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    bbq_roof:        { v: 'roof', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'no', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    elevation:       { v: 42, src: 'auto', at: '2026-07' },
    supermarket:     { v: 10, src: 'auto', at: '2026-07' },
    conveni:         { v: 6, src: 'auto', at: '2026-07' },
    ic:              { v: '長生IC 19分', src: 'auto', at: '2026-07' },
    station:         { v: '太東 6分', src: 'auto', at: '2026-07' },
    onsen:           { v: 19, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    bring_trash:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' },
    early_late:      { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.chiba-isumi-privatevilla.com/' }
  },

  "73": {  /* SANU 2nd Home 南アルプス1st */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052337/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 675, src: 'auto', at: '2026-07' },
    supermarket:     { v: 8, src: 'auto', at: '2026-07' },
    conveni:         { v: 8, src: 'auto', at: '2026-07' },
    ic:              { v: '八ヶ岳PA(下り) 20分', src: 'auto', at: '2026-07' },
    station:         { v: '日野春 11分', src: 'auto', at: '2026-07' },
    onsen:           { v: 7, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "74": {  /* SANU 2nd Home 八ヶ岳2nd */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'barrel', src: 'desk', at: '2026-07' },
    stove:           { v: 'gas', src: 'desk', at: '2026-07' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-07' },
    rest_chair:      { v: 'chair', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 1198, src: 'auto', at: '2026-07' },
    supermarket:     { v: 9, src: 'auto', at: '2026-07' },
    conveni:         { v: 7, src: 'auto', at: '2026-07' },
    ic:              { v: '八ヶ岳PA(下り) 16分', src: 'auto', at: '2026-07' },
    station:         { v: '甲斐大泉 7分', src: 'auto', at: '2026-07' },
    onsen:           { v: 7, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "75": {  /* SANU 2nd Home 八ヶ岳3rd */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052073/' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 1035, src: 'auto', at: '2026-07' },
    supermarket:     { v: 6, src: 'auto', at: '2026-07' },
    conveni:         { v: 2, src: 'auto', at: '2026-07' },
    ic:              { v: '八ヶ岳PA(下り) 10分', src: 'auto', at: '2026-07' },
    station:         { v: '甲斐大泉 3分', src: 'auto', at: '2026-07' },
    onsen:           { v: 3, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "76": {  /* SANU 2nd Home 河口湖2nd */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052074/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 1012, src: 'auto', at: '2026-07' },
    supermarket:     { v: 3, src: 'auto', at: '2026-07' },
    conveni:         { v: 3, src: 'auto', at: '2026-07' },
    ic:              { v: '富士吉田忍野スマートIC 15分', src: 'auto', at: '2026-07' },
    station:         { v: '河口湖 11分', src: 'auto', at: '2026-07' },
    onsen:           { v: 5, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "77": {  /* enico.Mt.Fuji smile */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 859, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 8分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "78": {  /* enico.Mt.Fuji Resort & Glamping */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 1029, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "79": {  /* est ed.1 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 989, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '八ヶ岳PA(下り) 9分', src: 'auto', at: '2026-07' },
    station:      { v: '甲斐大泉 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "80": {  /* 2gether foret */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 989, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '八ヶ岳PA(下り) 9分', src: 'auto', at: '2026-07' },
    station:      { v: '甲斐大泉 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "81": {  /* 古民家宿るうふ　織之家 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/shikinoie/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/shikinoie/' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    elevation:       { v: 485, src: 'auto', at: '2026-07' },
    supermarket:     { v: 14, src: 'auto', at: '2026-07' },
    conveni:         { v: 4, src: 'auto', at: '2026-07' },
    ic:              { v: '初狩PA(下り) 15分', src: 'auto', at: '2026-07' },
    station:         { v: '初狩 5分', src: 'auto', at: '2026-07' },
    onsen:           { v: 6, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/shikinoie/' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/shikinoie/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/shikinoie/' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/shikinoie/' }
  },

  "82": {  /* 古民家宿るうふ　祝之家 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/iwainoie/' },
    kitchen_type:    { v: 'gas', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/iwainoie/' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    elevation:       { v: 249, src: 'auto', at: '2026-07' },
    supermarket:     { v: 4, src: 'auto', at: '2026-07' },
    conveni:         { v: 1, src: 'auto', at: '2026-07' },
    ic:              { v: '田富東ランプ 5分', src: 'auto', at: '2026-07' },
    station:         { v: '東花輪 3分', src: 'auto', at: '2026-07' },
    onsen:           { v: 2, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/iwainoie/' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/iwainoie/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/iwainoie/' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://loof-inn.com/hotels/iwainoie/' }
  },

  "83": {  /* THE TIME FUJI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 860, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 16分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "84": {  /* mysa fuji */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 871, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 16分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "85": {  /* mysa yamanakako */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 1012, src: 'auto', at: '2026-07' },
    supermarket:  { v: 14, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '山中湖 23分', src: 'auto', at: '2026-07' },
    station:      { v: '寿 27分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "86": {  /* hotel norm. air */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 852, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "87": {  /* hotel norm. ao */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 855, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "88": {  /* hotel norm. fuji */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 850, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "89": {  /* 景雅 奥河口湖 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 860, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 18分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "90": {  /* totonoco 湖畔の隠れ家 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 837, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 17分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "91": {  /* ビジョングランピングリゾート山中湖 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 976, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 6分', src: 'auto', at: '2026-07' },
    station:      { v: '富士山 13分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "92": {  /* VILLA SAISON FUJI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 854, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "93": {  /* ヴィラグリファーム七里岩 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 516, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 7, src: 'auto', at: '2026-07' },
    ic:           { v: '韮崎IC 16分', src: 'auto', at: '2026-07' },
    station:      { v: '穴山 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "94": {  /* abrAsus hotel Fuji */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 977, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "95": {  /* 天空の温泉ヴィラ紬 河口湖 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type: { v: 'gas', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'no', src: 'desk', at: '2026-07' },
    elevation:    { v: 869, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田西桂SIC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' },
    sound_rule:   { v: 'night', src: 'desk', at: '2026-07' }
  },

  "96": {  /* yl&Co.Hotel in Mt.Fuji */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 978, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 12分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "97": {  /* VILLA　SUOMI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 997, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '須走IC 17分', src: 'auto', at: '2026-07' },
    station:      { v: '富士山 20分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "98": {  /* SILVER SPRAY 山中湖 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 988, src: 'auto', at: '2026-07' },
    supermarket:  { v: 13, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '山中湖 22分', src: 'auto', at: '2026-07' },
    station:      { v: '寿 26分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "99": {  /* ハンズアウトドアリゾート */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://glampicks.jp/glamping/g46375/' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 928, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "100": {  /* MT.FUJI SKY CABIN */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 797, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '河口湖IC 12分', src: 'auto', at: '2026-07' },
    station:      { v: '月江寺 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "101": {  /* KURA YARD */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 840, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田西桂SIC 11分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "102": {  /* SAUNEA白州 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'hut', src: 'desk', at: '2026-07' },
    sauna_cap:       { v: 6, src: 'desk', at: '2026-07' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-07' },
    rest_chair:      { v: 'chair', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-07' },
    kitchen_burners: { v: 2, src: 'desk', at: '2026-07' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 698, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 5, src: 'auto', at: '2026-07' },
    ic:              { v: '八ヶ岳PA(下り) 17分', src: 'auto', at: '2026-07' },
    station:         { v: '日野春 11分', src: 'auto', at: '2026-07' },
    onsen:           { v: 5, src: 'auto', at: '2026-07' }
  },

  "103": {  /* Private villa FujiNagi */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 864, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田西桂SIC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "104": {  /* 憩~ikoi_Fuji */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 859, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '河口湖IC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "105": {  /* BLANC FUJI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 858, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山中湖 7分', src: 'auto', at: '2026-07' },
    station:      { v: '富士山 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "106": {  /* 郷音 -G.O.A.T.- The Summit Club */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 16, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 542, src: 'auto', at: '2026-07' },
    supermarket:  { v: 19, src: 'auto', at: '2026-07' },
    conveni:      { v: 12, src: 'auto', at: '2026-07' },
    ic:           { v: '都留IC 32分', src: 'auto', at: '2026-07' },
    station:      { v: '禾生 14分', src: 'auto', at: '2026-07' },
    onsen:        { v: 12, src: 'auto', at: '2026-07' }
  },

  "107": {  /* ReTune | SPA & SAUNA / VILLA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 906, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '八ヶ岳PA(下り) 7分', src: 'auto', at: '2026-07' },
    station:      { v: '甲斐大泉 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "108": {  /* THE THIRD PLACE Mt.Fuji */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 970, src: 'auto', at: '2026-07' },
    supermarket:  { v: 15, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '内野IC 12分', src: 'auto', at: '2026-07' },
    station:      { v: '甲斐常葉 26分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "109": {  /* Kakoi 雪嶺 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 1052, src: 'auto', at: '2026-07' },
    supermarket:  { v: 15, src: 'auto', at: '2026-07' },
    conveni:      { v: 12, src: 'auto', at: '2026-07' },
    ic:           { v: '内野IC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '市ノ瀬 26分', src: 'auto', at: '2026-07' },
    onsen:        { v: 12, src: 'auto', at: '2026-07' }
  },

  "110": {  /* THE BLISS FUJI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 1037, src: 'auto', at: '2026-07' },
    supermarket:  { v: 16, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '山中湖 25分', src: 'auto', at: '2026-07' },
    station:      { v: '駿河小山 29分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "111": {  /* HOTEL SEION FUJI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    elevation:    { v: 993, src: 'auto', at: '2026-07' },
    supermarket:  { v: 16, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '山中湖 25分', src: 'auto', at: '2026-07' },
    station:      { v: '駿河小山 33分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "112": {  /* private villa ietona */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 877, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 9分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "113": {  /* ASH Villa 富士河口湖 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 1007, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '富士吉田忍野スマートIC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '河口湖 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "114": {  /* エンゼルフォレスト那須 */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 654, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '那須高原スマートIC 22分', src: 'auto', at: '2026-07' },
    station:      { v: '黒田原 16分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "115": {  /* 有形文化財ホテル 飯塚邸 */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://travel.yahoo.co.jp/00050899/' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    elevation:    { v: 119, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '野高谷北ランプ 38分', src: 'auto', at: '2026-07' },
    station:      { v: '烏山 14分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "116": {  /* Kito NASU */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 319, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '黒磯板室IC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '黒磯 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "117": {  /* THE SECOND Nasukogen Forest House */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    stove:         { v: 'electric', src: 'desk', at: '2026-08', url: 'https://www.thesecondhotels.com/nasukogen-forest-house' },
    villa_type:    { v: 'multi', src: 'desk', at: '2026-08', url: 'https://www.thesecondhotels.com/nasukogen-forest-house' },
    kitchen_type:  { v: 'ih', src: 'desk', at: '2026-08', url: 'https://www.thesecondhotels.com/nasukogen-forest-house' },
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.thesecondhotels.com/nasukogen-forest-house' },
    elevation:     { v: 490, src: 'auto', at: '2026-07' },
    supermarket:   { v: 4, src: 'auto', at: '2026-07' },
    conveni:       { v: 4, src: 'auto', at: '2026-07' },
    ic:            { v: '那須高原スマートIC 17分', src: 'auto', at: '2026-07' },
    station:       { v: '高久 16分', src: 'auto', at: '2026-07' },
    onsen:         { v: 7, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.thesecondhotels.com/nasukogen-forest-house' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://www.thesecondhotels.com/nasukogen-forest-house' }
  },

  "118": {  /* SANU 2nd Home 那須1st */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052026/11555802/10277047/' },
    sauna_type:      { v: 'barrel', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 690, src: 'auto', at: '2026-07' },
    supermarket:     { v: 7, src: 'auto', at: '2026-07' },
    conveni:         { v: 8, src: 'auto', at: '2026-07' },
    ic:              { v: '那須高原スマートIC 23分', src: 'auto', at: '2026-07' },
    station:         { v: '高久 22分', src: 'auto', at: '2026-07' },
    onsen:           { v: 4, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "119": {  /* SANU 2nd Home 那須2nd */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://travel.yahoo.co.jp/00052027/room/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 834, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 5, src: 'auto', at: '2026-07' },
    ic:              { v: '那須高原スマートIC 22分', src: 'auto', at: '2026-07' },
    station:         { v: '高久 22分', src: 'auto', at: '2026-07' },
    onsen:           { v: 6, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "120": {  /* SANU 2nd Home 那須3rd */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052290/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 851, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 5, src: 'auto', at: '2026-07' },
    ic:              { v: '那須高原スマートIC 23分', src: 'auto', at: '2026-07' },
    station:         { v: '高久 22分', src: 'auto', at: '2026-07' },
    onsen:           { v: 6, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "121": {  /* COCO VILLA 那須高原 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 498, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '那須高原スマートIC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '高久 15分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "122": {  /* Earthboat Nasu */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 812, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '那須高原スマートIC 21分', src: 'auto', at: '2026-07' },
    station:      { v: '高久 20分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "123": {  /* RIVER VIEW HOUSE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 533, src: 'auto', at: '2026-07' },
    supermarket:  { v: 17, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '黒磯板室IC 22分', src: 'auto', at: '2026-07' },
    station:      { v: '上三依塩原温泉口 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "124": {  /* 北欧伝説 ドワーフの村 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 428, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '那須高原スマートIC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '高久 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "125": {  /* 森deワーケなすっぽ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 459, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '那須高原スマートIC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '高久 12分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "126": {  /* 御宿 憩（OYADO IKOI） */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    elevation:    { v: 401, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '日光口PA(下り) 4分', src: 'auto', at: '2026-07' },
    station:      { v: '今市 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "127": {  /* VillaEL5 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 28, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 384, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '土沢IC 8分', src: 'auto', at: '2026-07' },
    station:      { v: '下今市 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "128": {  /* Haga Farm＆Glamping（芳賀ファーム&グランピング） */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://hagafarm.com/experience/' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 131, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '野高谷北ランプ 10分', src: 'auto', at: '2026-07' },
    station:      { v: '大金 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "129": {  /* 和モダングランピング｜NAGOMI CAMP */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://www.glamping-tochigi.com/' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 429, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '黒磯板室IC 14分', src: 'auto', at: '2026-07' },
    station:      { v: '那須塩原 17分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "130": {  /* 那須温泉グランピング Nenn（ネン） */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://travel.rakuten.co.jp/HOTEL/184489/184489.html' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 434, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '那須高原スマートIC 11分', src: 'auto', at: '2026-07' },
    station:      { v: '高久 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "131": {  /* LEVATA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 530, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 8, src: 'auto', at: '2026-07' },
    ic:           { v: '黒磯板室IC 21分', src: 'auto', at: '2026-07' },
    station:      { v: '高久 22分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "132": {  /* GEOSPOT MOTOHAKONE A */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 870, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '小涌谷 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "133": {  /* GEOSPOT MOTOHAKONE B */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'cold', src: 'desk', at: '2026-08', url: 'https://geo-spot.com/motohakone/' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-08', url: 'https://geo-spot.com/motohakone/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 871, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '小涌谷 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "134": {  /* GEOSPOT MOTOHAKONE C */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'cold', src: 'desk', at: '2026-08', url: 'https://geo-spot.com/motohakone/' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-08', url: 'https://geo-spot.com/motohakone/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 870, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '小涌谷 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "135": {  /* ASNOVA RESORT FOLQ HAKONE GORA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 772, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "136": {  /* ASNOVA RESORT NOIE HAKONE SENGOKUHARA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 666, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 21分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 12分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "137": {  /* P's Wood 箱根仙石原 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    elevation:    { v: 726, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "138": {  /* Casablanca Villa Hakone */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 852, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 8分', src: 'auto', at: '2026-07' },
    station:      { v: '小涌谷 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "139": {  /* moon hakone */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 10, src: 'desk', at: '2026-07' },
    elevation:    { v: 247, src: 'auto', at: '2026-07' },
    supermarket:  { v: 14, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '須雲川IC 7分', src: 'auto', at: '2026-07' },
    station:      { v: '箱根湯本 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "140": {  /* ルクス箱根湯本 LUX HAKONE YUMOTO */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 151, src: 'auto', at: '2026-07' },
    supermarket:  { v: 12, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '山崎IC 4分', src: 'auto', at: '2026-07' },
    station:      { v: '箱根湯本 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "141": {  /* koti hakone */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 26, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 689, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 20分', src: 'auto', at: '2026-07' },
    station:      { v: '上強羅 12分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "142": {  /* プライベートリゾート仙居 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 620, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '須雲川IC 21分', src: 'auto', at: '2026-07' },
    station:      { v: '公園上 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "143": {  /* mysa hakone */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 563, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '須雲川IC 20分', src: 'auto', at: '2026-07' },
    station:      { v: '彫刻の森 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "144": {  /* シエロ箱根仙石原 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    elevation:    { v: 851, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '箱根峠出入口 14分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "145": {  /* ICHI-VILLA CROSSROAD HAKONE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 652, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 18分', src: 'auto', at: '2026-07' },
    station:      { v: '上強羅 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "146": {  /* TIMeSCAPE -hakone- */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 316, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '須雲川IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '大平台 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "147": {  /* 箱根芦ノ湖ゴルフヴィラ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 734, src: 'auto', at: '2026-07' },
    supermarket:  { v: 12, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 1分', src: 'auto', at: '2026-07' },
    station:      { v: '小涌谷 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "148": {  /* エスパシオ箱根迎賓館　麟鳳亀龍 */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-07' },
    capacity:     { v: 2, src: 'desk', at: '2026-07' },
    elevation:    { v: 414, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '須雲川IC 16分', src: 'auto', at: '2026-07' },
    station:      { v: '宮ノ下 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "149": {  /* MOROISOSO-サウナ＆温水プール付きラグジュアリーヴィラ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 21, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '林IC 25分', src: 'auto', at: '2026-07' },
    station:      { v: '三崎口 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "150": {  /* 3rd HOUSE INAMURAGASAKI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 5, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '釜利谷JCT 19分', src: 'auto', at: '2026-07' },
    station:      { v: '稲村ヶ崎 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "151": {  /* 琥珀-AMBER- */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '釜利谷JCT 16分', src: 'auto', at: '2026-07' },
    station:      { v: '和田塚 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "152": {  /* NIWA　KAMAKURA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 25, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '釜利谷JCT 15分', src: 'auto', at: '2026-07' },
    station:      { v: '北鎌倉 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "153": {  /* UMITO VILLA KAMAKURA ZAIMOKUZA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 7, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '釜利谷JCT 15分', src: 'auto', at: '2026-07' },
    station:      { v: '由比ヶ浜 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "154": {  /* LULLA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 4, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '釜利谷JCT 16分', src: 'auto', at: '2026-07' },
    station:      { v: '鎌倉 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "155": {  /* SAJIMA Funny house */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 37, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '林IC 14分', src: 'auto', at: '2026-07' },
    station:      { v: '衣笠 13分', src: 'auto', at: '2026-07' },
    onsen:        { v: 14, src: 'auto', at: '2026-07' }
  },

  "156": {  /* MONS GORA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 705, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 14分', src: 'auto', at: '2026-07' },
    station:      { v: '上強羅 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "157": {  /* TANZAWA seven lanes by DAICHI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 390, src: 'auto', at: '2026-07' },
    supermarket:  { v: 21, src: 'auto', at: '2026-07' },
    conveni:      { v: 17, src: 'auto', at: '2026-07' },
    ic:           { v: '鮎沢PA(上り) 37分', src: 'auto', at: '2026-07' },
    station:      { v: '谷峨 12分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "158": {  /* GIFTHOUSE 三浦 諸磯 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 3, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '林IC 26分', src: 'auto', at: '2026-07' },
    station:      { v: '三崎口 12分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "159": {  /* 葉山THE・TERRACE　HOUSE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 13, src: 'desk', at: '2026-07' },
    elevation:    { v: 4, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '逗子IC 15分', src: 'auto', at: '2026-07' },
    station:      { v: '逗子・葉山 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 12, src: 'auto', at: '2026-07' }
  },

  "160": {  /* 雅・仙石原 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 14, src: 'desk', at: '2026-07' },
    elevation:    { v: 688, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 22分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "161": {  /* Oceanfront Villa Hale Kahakai */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '衣笠IC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '津久井浜 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "162": {  /* プライベートヴィラ愛川 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 116, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '相模原愛川IC 26分', src: 'auto', at: '2026-07' },
    station:      { v: 'ダム下 山麓 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 21, src: 'auto', at: '2026-07' }
  },

  "163": {  /* 箱根温泉別邸白鷺 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 709, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "164": {  /* HAKONE DOMA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    elevation:    { v: 727, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 7, src: 'auto', at: '2026-07' },
    ic:           { v: '箱根峠IC 11分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "165": {  /* 箱根懐來 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 690, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 21分', src: 'auto', at: '2026-07' },
    station:      { v: '上強羅 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "166": {  /* in the meantime */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 704, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '中強羅 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "167": {  /* 箱根リゾートyamaki */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 654, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 18分', src: 'auto', at: '2026-07' },
    station:      { v: '上強羅 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "168": {  /* 湯屋　やまざくら */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://hakoneyamazakura.com' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    elevation:    { v: 642, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 18分', src: 'auto', at: '2026-07' },
    station:      { v: '上強羅 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "169": {  /* 湯と灯りに包まれる別世界 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 14, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '茅ヶ崎中央IC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '片瀬江ノ島 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "170": {  /* Six on the Beach TORAMII -Enoshima- */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    sauna_cap:    { v: 6, src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '茅ヶ崎中央IC 18分', src: 'auto', at: '2026-07' },
    station:      { v: '片瀬江ノ島 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' },
    fee_bbq:      { v: 'incl', src: 'desk', at: '2026-07' }
  },

  "171": {  /* Noёl HAKONE GENSEN */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 840, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 16分', src: 'auto', at: '2026-07' },
    station:      { v: '早雲山 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "172": {  /* Oyado S */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    chiller:      { v: 'yes', src: 'desk', at: '2026-07' },
    water_temp:   { v: '10〜18', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 829, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '芦ノ湖大観IC 8分', src: 'auto', at: '2026-07' },
    station:      { v: '小涌谷 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "173": {  /* 軽井沢365 フォレストガーデン八風台 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'hut', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    stove:           { v: 'wood', src: 'desk', at: '2026-07' },
    sauna_hours:     { v: 'limited', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    rest_chair:      { v: 'infinity', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    comfort_cap:     { v: 6, src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    steps:           { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    elevation:       { v: 962, src: 'auto', at: '2026-07' },
    supermarket:     { v: 9, src: 'auto', at: '2026-07' },
    conveni:         { v: 8, src: 'auto', at: '2026-07' },
    ic:              { v: '佐久平スマートIC 28分', src: 'auto', at: '2026-07' },
    station:         { v: '中軽井沢 10分', src: 'auto', at: '2026-07' },
    onsen:           { v: 1, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    bring_trash:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' },
    firewood_fee:    { v: 'incl', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/happudai' }
  },

  "174": {  /* 軽井沢365 プレイガーデン大日向 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'indoor', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    stove:           { v: 'electric', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-07' },
    rest_chair:      { v: 'bench', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    capacity:        { v: 7, src: 'desk', at: '2026-07' },
    comfort_cap:     { v: 6, src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    elevation:       { v: 1063, src: 'auto', at: '2026-07' },
    supermarket:     { v: 6, src: 'auto', at: '2026-07' },
    conveni:         { v: 3, src: 'auto', at: '2026-07' },
    ic:              { v: '佐久小諸JCT 15分', src: 'auto', at: '2026-07' },
    station:         { v: '信濃追分 5分', src: 'auto', at: '2026-07' },
    onsen:           { v: 5, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    bring_trash:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' },
    firewood_fee:    { v: 'incl', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/ohinata' }
  },

  "175": {  /* 軽井沢365 リバーサイドヴィラ八風台 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    stove:           { v: 'electric', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    rest_chair:      { v: 'infinity', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    comfort_cap:     { v: 10, src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    elevation:       { v: 958, src: 'auto', at: '2026-07' },
    supermarket:     { v: 9, src: 'auto', at: '2026-07' },
    conveni:         { v: 8, src: 'auto', at: '2026-07' },
    ic:              { v: '佐久平スマートIC 28分', src: 'auto', at: '2026-07' },
    station:         { v: '中軽井沢 10分', src: 'auto', at: '2026-07' },
    onsen:           { v: 1, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    bring_trash:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' },
    firewood_fee:    { v: 'incl', src: 'desk', at: '2026-08', url: 'https://karuizawa365.jp/stay/riversidevilla' }
  },

  "176": {  /* SANU 2nd Home 北軽井沢2nd */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052029/11555912/10277648/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 1164, src: 'auto', at: '2026-07' },
    supermarket:     { v: 6, src: 'auto', at: '2026-07' },
    conveni:         { v: 5, src: 'auto', at: '2026-07' },
    ic:              { v: '小諸IC 43分', src: 'auto', at: '2026-07' },
    station:         { v: '大前 10分', src: 'auto', at: '2026-07' },
    onsen:           { v: 10, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "177": {  /* SANU 2nd Home 蓼科1st */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052266/11641728/10292977/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 1452, src: 'auto', at: '2026-07' },
    supermarket:     { v: 10, src: 'auto', at: '2026-07' },
    conveni:         { v: 5, src: 'auto', at: '2026-07' },
    ic:              { v: '中央道原PA(上り) 27分', src: 'auto', at: '2026-07' },
    station:         { v: '茅野 17分', src: 'auto', at: '2026-07' },
    onsen:           { v: 5, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "178": {  /* SANU 2nd Home 軽井沢2nd */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052415/' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 981, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 4, src: 'auto', at: '2026-07' },
    ic:              { v: '佐久小諸JCT 13分', src: 'auto', at: '2026-07' },
    station:         { v: '信濃追分 6分', src: 'auto', at: '2026-07' },
    onsen:           { v: 7, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "179": {  /* SANU 2nd Home 白馬1st */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.ikyu.com/00052076/' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 791, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 3, src: 'auto', at: '2026-07' },
    ic:              { v: '更埴IC 50分', src: 'auto', at: '2026-07' },
    station:         { v: '白馬 5分', src: 'auto', at: '2026-07' },
    onsen:           { v: 3, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "180": {  /* GLAMDAY STYLE HOTEL SUITE 山ノ麓 */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    stove:         { v: 'wood', src: 'desk', at: '2026-07' },
    capacity:      { v: 7, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://gs-hotelsuite.jp/yamanofumoto/' },
    elevation:     { v: 943, src: 'auto', at: '2026-07' },
    supermarket:   { v: 2, src: 'auto', at: '2026-07' },
    conveni:       { v: 2, src: 'auto', at: '2026-07' },
    ic:            { v: '横川SA(上り) 25分', src: 'auto', at: '2026-07' },
    station:       { v: '軽井沢 2分', src: 'auto', at: '2026-07' },
    onsen:         { v: 9, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://gs-hotelsuite.jp/yamanofumoto/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://gs-hotelsuite.jp/yamanofumoto/' }
  },

  "181": {  /* GLAMDAY STYLE HOTEL SUITE 川ノ音 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 973, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '横川SA(上り) 25分', src: 'auto', at: '2026-07' },
    station:      { v: '軽井沢 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "182": {  /* The Aurora Chalet */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 776, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '更埴IC 48分', src: 'auto', at: '2026-07' },
    station:      { v: '飯森 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "183": {  /* Hakuba Amber Resort */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 775, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '更埴IC 48分', src: 'auto', at: '2026-07' },
    station:      { v: '飯森 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "184": {  /* Hakuba Jolie Maison */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 719, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '更埴IC 48分', src: 'auto', at: '2026-07' },
    station:      { v: '白馬 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "185": {  /* SAUNA VILLA 然 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 372, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '大豆島IC 8分', src: 'auto', at: '2026-07' },
    station:      { v: '権堂 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "186": {  /* Lakeside villa SUI HAKUBA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 823, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '筑北PA(下り) 41分', src: 'auto', at: '2026-07' },
    station:      { v: '簗場 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "187": {  /* GREENSEED軽井沢 */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://greenseed-villa.com/rooms/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 970, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久小諸JCT 11分', src: 'auto', at: '2026-07' },
    station:      { v: '信濃追分 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "188": {  /* COCO VILLA 軽井沢 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 937, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久平スマートIC 31分', src: 'auto', at: '2026-07' },
    station:      { v: '中軽井沢 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' },
    fee_bbq:      { v: 'incl', src: 'desk', at: '2026-07' }
  },

  "189": {  /* Tatehata House 北軽井沢 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 1086, src: 'auto', at: '2026-07' },
    supermarket:  { v: 12, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '横川SA(上り) 41分', src: 'auto', at: '2026-07' },
    station:      { v: '万座・鹿沢口 13分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "190": {  /* Hygge chalet hakuba（ヒュッゲ シャレー） */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    stove:           { v: 'wood', src: 'desk', at: '2026-07' },
    sauna_temp:      { v: 85, src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    sauna_cap:       { v: 8, src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    sauna_hours:     { v: 'limited', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    water_src:       { v: 'spring', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    rest_chair:      { v: 'infinity', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    firepit:         { v: 'stand', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    elevation:       { v: 786, src: 'auto', at: '2026-07' },
    supermarket:     { v: 5, src: 'auto', at: '2026-07' },
    conveni:         { v: 2, src: 'auto', at: '2026-07' },
    ic:              { v: '更埴IC 49分', src: 'auto', at: '2026-07' },
    station:         { v: '飯森 6分', src: 'auto', at: '2026-07' },
    onsen:           { v: 5, src: 'auto', at: '2026-07' },
    bring_seasoning: { v: 'bring', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' },
    firewood_fee:    { v: 'extra', src: 'desk', at: '2026-08', url: 'https://chalet-hakuba-hygge.com/system/' }
  },

  "191": {  /* 軽井沢 HOUSE VILLA */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://karuizawa-house-villa.com' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 1034, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久小諸JCT 14分', src: 'auto', at: '2026-07' },
    station:      { v: '信濃追分 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "192": {  /* ポーラーハウスカナディアン南軽井沢1 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.polar-resort.com/建物別詳細予約' },
    bbq_roof:     { v: 'open', src: 'desk', at: '2026-08', url: 'https://www.polar-resort.com/建物別詳細予約' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'no', src: 'desk', at: '2026-08', url: 'https://www.polar-resort.com/建物別詳細予約' },
    elevation:    { v: 939, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久平スマートIC 25分', src: 'auto', at: '2026-07' },
    station:      { v: '軽井沢 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "193": {  /* SAUNA FOREST CABIN 軽井沢御代田 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    sauna_cap:    { v: 6, src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 772, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久平スマートIC 12分', src: 'auto', at: '2026-07' },
    station:      { v: '御代田 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' },
    fee_bbq:      { v: 'extra', src: 'desk', at: '2026-07' }
  },

  "194": {  /* 海野宿一棟貸し宿　上州屋 */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'indoor', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    stove:           { v: 'electric', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    sauna_temp:      { v: 90, src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    sauna_hours:     { v: 'limited', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/stay' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:      { v: 'multi', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    capacity:        { v: 5, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    steps:           { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    elevation:       { v: 490, src: 'auto', at: '2026-07' },
    supermarket:     { v: 2, src: 'auto', at: '2026-07' },
    conveni:         { v: 1, src: 'auto', at: '2026-07' },
    ic:              { v: '上田菅平IC 13分', src: 'auto', at: '2026-07' },
    station:         { v: '田中 4分', src: 'auto', at: '2026-07' },
    onsen:           { v: 4, src: 'auto', at: '2026-07' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/rooms' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/stay' },
    late_arrival:    { v: 'no', src: 'desk', at: '2026-08', url: 'https://joshuya-unnojuku.jp/stay' }
  },

  "195": {  /* Earthboat Kurohime */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 740, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '信濃町IC 9分', src: 'auto', at: '2026-07' },
    station:      { v: '黒姫 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "196": {  /* Karuizawa Luxe Villa */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 1075, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久小諸JCT 16分', src: 'auto', at: '2026-07' },
    station:      { v: '信濃追分 6分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "197": {  /* トライハク軽井沢 神楽-かぐら- */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 1066, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久小諸JCT 16分', src: 'auto', at: '2026-07' },
    station:      { v: '信濃追分 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "198": {  /* T&A Resort&Sauna KARUIZAWA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 11, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 925, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '佐久小諸JCT 12分', src: 'auto', at: '2026-07' },
    station:      { v: '御代田 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "199": {  /* 北軽井沢 貸別荘 FARMSIDE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 1172, src: 'auto', at: '2026-07' },
    supermarket:  { v: 13, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '小諸IC 40分', src: 'auto', at: '2026-07' },
    station:      { v: '万座・鹿沢口 15分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "200": {  /* enukoti（エヌコティ） */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 1192, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 7, src: 'auto', at: '2026-07' },
    ic:           { v: '中央道原PA(下り) 12分', src: 'auto', at: '2026-07' },
    station:      { v: '富士見 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "201": {  /* キュレーション熱海桃乃八庵 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type: { v: 'ih', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 83, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '伊豆山港 4分', src: 'auto', at: '2026-07' },
    station:      { v: '熱海 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "202": {  /* キュレーション熱海須藤水園 */
    kitchen_type: { v: 'ih', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 72, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '伊豆山港 4分', src: 'auto', at: '2026-07' },
    station:      { v: '熱海 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "203": {  /* キュレーション熱海桃山雅苑 */
    kitchen_type: { v: 'ih', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 126, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '伊豆山港 4分', src: 'auto', at: '2026-07' },
    station:      { v: '熱海 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "204": {  /* オーシャンビュー南熱海 */
    capacity:      { v: 9, src: 'desk', at: '2026-07' },
    comfort_cap:   { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'no', src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:     { v: 290, src: 'auto', at: '2026-07' },
    supermarket:   { v: 10, src: 'auto', at: '2026-07' },
    conveni:       { v: 8, src: 'auto', at: '2026-07' },
    ic:            { v: '山伏峠IC 21分', src: 'auto', at: '2026-07' },
    station:       { v: '網代 8分', src: 'auto', at: '2026-07' },
    onsen:         { v: 13, src: 'auto', at: '2026-07' },
    winter_access: { v: 'tire', src: 'desk', at: '2026-07' }
  },

  "205": {  /* オーシャンビュー熱海自然郷 */
    bbq_roof:    { v: 'none', src: 'desk', at: '2026-07' },
    capacity:    { v: 10, src: 'desk', at: '2026-07' },
    comfort_cap: { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:      { v: 'no', src: 'desk', at: '2026-07' },
    elevation:   { v: 508, src: 'auto', at: '2026-07' },
    supermarket: { v: 13, src: 'auto', at: '2026-07' },
    conveni:     { v: 11, src: 'auto', at: '2026-07' },
    ic:          { v: '玄岳IC 7分', src: 'auto', at: '2026-07' },
    station:     { v: '伊豆多賀 12分', src: 'auto', at: '2026-07' },
    onsen:       { v: 13, src: 'auto', at: '2026-07' }
  },

  "206": {  /* オーシャンビュー熱海自然楼 */
    bbq_roof:    { v: 'none', src: 'desk', at: '2026-07' },
    capacity:    { v: 10, src: 'desk', at: '2026-07' },
    pet_ok:      { v: 'no', src: 'desk', at: '2026-07' },
    wifi:        { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:   { v: 322, src: 'auto', at: '2026-07' },
    supermarket: { v: 9, src: 'auto', at: '2026-07' },
    conveni:     { v: 10, src: 'auto', at: '2026-07' },
    ic:          { v: '玄岳IC 9分', src: 'auto', at: '2026-07' },
    station:     { v: '伊豆多賀 8分', src: 'auto', at: '2026-07' },
    onsen:       { v: 12, src: 'auto', at: '2026-07' }
  },

  "207": {  /* パノーラ伊豆赤沢 */
    kitchen_type:    { v: 'both', src: 'desk', at: '2026-07' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-07' },
    bbq_roof:        { v: 'none', src: 'desk', at: '2026-07' },
    capacity:        { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'no', src: 'desk', at: '2026-07' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 200, src: 'auto', at: '2026-07' },
    supermarket:     { v: 7, src: 'auto', at: '2026-07' },
    conveni:         { v: 7, src: 'auto', at: '2026-07' },
    ic:              { v: '河津七滝IC 48分', src: 'auto', at: '2026-07' },
    station:         { v: '伊豆高原 8分', src: 'auto', at: '2026-07' },
    onsen:           { v: 6, src: 'auto', at: '2026-07' }
  },

  "208": {  /* パノーラ熱海桜沢 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 231, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '玄岳IC 9分', src: 'auto', at: '2026-07' },
    station:      { v: '来宮 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "209": {  /* 伊豆高原プライム */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'gas', src: 'desk', at: '2026-07' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-07' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 202, src: 'auto', at: '2026-07' },
    supermarket:     { v: 6, src: 'auto', at: '2026-07' },
    conveni:         { v: 1, src: 'auto', at: '2026-07' },
    ic:              { v: '大平IC 43分', src: 'auto', at: '2026-07' },
    station:         { v: '城ヶ崎海岸 5分', src: 'auto', at: '2026-07' },
    onsen:           { v: 4, src: 'auto', at: '2026-07' }
  },

  "210": {  /* 熱海オーシャンハウス */
    bbq_roof:      { v: 'none', src: 'desk', at: '2026-07' },
    capacity:      { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'no', src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:     { v: 439, src: 'auto', at: '2026-07' },
    supermarket:   { v: 12, src: 'auto', at: '2026-07' },
    conveni:       { v: 11, src: 'auto', at: '2026-07' },
    ic:            { v: '玄岳IC 7分', src: 'auto', at: '2026-07' },
    station:       { v: '伊豆多賀 11分', src: 'auto', at: '2026-07' },
    onsen:         { v: 13, src: 'auto', at: '2026-07' },
    winter_access: { v: 'tire', src: 'desk', at: '2026-07' }
  },

  "211": {  /* オーシャンテラスAtami */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_cap:    { v: 1, src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'no', src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 462, src: 'auto', at: '2026-07' },
    supermarket:  { v: 13, src: 'auto', at: '2026-07' },
    conveni:      { v: 11, src: 'auto', at: '2026-07' },
    ic:           { v: '玄岳IC 8分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆多賀 13分', src: 'auto', at: '2026-07' },
    onsen:        { v: 13, src: 'auto', at: '2026-07' }
  },

  "212": {  /* 熱海リゾート */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'indoor', src: 'desk', at: '2026-07' },
    sauna_cap:       { v: 2, src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-07' },
    kitchen_burners: { v: 2, src: 'desk', at: '2026-07' },
    capacity:        { v: 9, src: 'desk', at: '2026-07' },
    elevation:       { v: 304, src: 'auto', at: '2026-07' },
    supermarket:     { v: 9, src: 'auto', at: '2026-07' },
    conveni:         { v: 10, src: 'auto', at: '2026-07' },
    ic:              { v: '玄岳IC 9分', src: 'auto', at: '2026-07' },
    station:         { v: '伊豆多賀 8分', src: 'auto', at: '2026-07' },
    onsen:           { v: 11, src: 'auto', at: '2026-07' },
    late_arrival:    { v: 'ok', src: 'desk', at: '2026-07' }
  },

  "213": {  /* 熱海別邸　双梅庵 */
    capacity:    { v: 4, src: 'desk', at: '2026-07' },
    wifi:        { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:   { v: 105, src: 'auto', at: '2026-07' },
    supermarket: { v: 3, src: 'auto', at: '2026-07' },
    conveni:     { v: 3, src: 'auto', at: '2026-07' },
    ic:          { v: '伊豆山港 7分', src: 'auto', at: '2026-07' },
    station:     { v: '来宮 3分', src: 'auto', at: '2026-07' },
    onsen:       { v: 3, src: 'auto', at: '2026-07' }
  },

  "214": {  /* マイグレICE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    water_src:    { v: 'well', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 256, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "215": {  /* マイグレテラス */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    water_src:    { v: 'well', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 250, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "216": {  /* マイグレ天 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 333, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 42分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "217": {  /* マイグレフラット */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    water_src:    { v: 'well', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 250, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "218": {  /* マイグレ600 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 254, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "219": {  /* マイグレIKKI */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 10, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 252, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "220": {  /* マイグレKENKEN */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 253, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "221": {  /* マイグレYEBISU */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    sauna_cap:    { v: 9, src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    water_src:    { v: 'well', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 234, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "222": {  /* マイグレ海の声 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 18, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 47分', src: 'auto', at: '2026-07' },
    station:      { v: '城ヶ崎海岸 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "223": {  /* マイグレケニーズハウス */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'indoor', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 16, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 249, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "224": {  /* マイグレchillax */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'indoor', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 201, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 6, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 44分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆大川 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "225": {  /* マイグレHOODSTAR */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 226, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 38分', src: 'auto', at: '2026-07' },
    station:      { v: '川奈 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "226": {  /* マイグレアトリエ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 253, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "227": {  /* マイグレA5 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 254, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "228": {  /* マイグレパノラマ */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'indoor', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    wifi:         { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 252, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 39分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "229": {  /* WEAZER西伊豆 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    elevation:    { v: 85, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 24分', src: 'auto', at: '2026-07' },
    station:      { v: '修善寺 28分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "230": {  /* WEAZER西伊豆 廻 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 46, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 26分', src: 'auto', at: '2026-07' },
    station:      { v: '修善寺 30分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "231": {  /* Hiire IZU FUTO */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:      { v: 8, src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' },
    elevation:     { v: 289, src: 'auto', at: '2026-07' },
    supermarket:   { v: 6, src: 'auto', at: '2026-07' },
    conveni:       { v: 2, src: 'auto', at: '2026-07' },
    ic:            { v: '大平IC 41分', src: 'auto', at: '2026-07' },
    station:       { v: '富戸 5分', src: 'auto', at: '2026-07' },
    onsen:         { v: 4, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' }
  },

  "232": {  /* Hiire IZU OLIVE */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:      { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' },
    elevation:     { v: 103, src: 'auto', at: '2026-07' },
    supermarket:   { v: 2, src: 'auto', at: '2026-07' },
    conveni:       { v: 1, src: 'auto', at: '2026-07' },
    ic:            { v: '大平IC 44分', src: 'auto', at: '2026-07' },
    station:       { v: '伊豆高原 3分', src: 'auto', at: '2026-07' },
    onsen:         { v: 2, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' }
  },

  "233": {  /* Hiire IZU OMURO */
    sauna_exists:  { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:      { v: 6, src: 'desk', at: '2026-07' },
    wifi:          { v: 'yes', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' },
    elevation:     { v: 231, src: 'auto', at: '2026-07' },
    supermarket:   { v: 3, src: 'auto', at: '2026-07' },
    conveni:       { v: 3, src: 'auto', at: '2026-07' },
    ic:            { v: '大平IC 40分', src: 'auto', at: '2026-07' },
    station:       { v: '伊豆高原 5分', src: 'auto', at: '2026-07' },
    onsen:         { v: 4, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://hi-ire.com/stay' }
  },

  "234": {  /* COCO VILLA 伊豆赤沢 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'hut', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 84, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '河津七滝IC 46分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆高原 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "235": {  /* COCO VILLA 大室山 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 423, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 7, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 38分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "236": {  /* Tiny Base The MOUNTAiN */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 41, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 14分', src: 'auto', at: '2026-07' },
    station:      { v: '河津 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "237": {  /* Tiny Base The Irita-hama */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 4, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆急下田 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "238": {  /* 月と太陽 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 443, src: 'auto', at: '2026-07' },
    supermarket:  { v: 12, src: 'auto', at: '2026-07' },
    conveni:      { v: 10, src: 'auto', at: '2026-07' },
    ic:           { v: '玄岳IC 6分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆多賀 11分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' }
  },

  "239": {  /* AMAO VILLA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 199, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 42分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "240": {  /* Wellリゾート富士 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    elevation:    { v: 628, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 6, src: 'auto', at: '2026-07' },
    ic:           { v: '足柄SA/スマートIC(上り) 8分', src: 'auto', at: '2026-07' },
    station:      { v: '御殿場 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "241": {  /* Poolen ITO */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 28, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 48分', src: 'auto', at: '2026-07' },
    station:      { v: '城ヶ崎海岸 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "242": {  /* the villa Oka 伊豆高原温泉 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 123, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 46分', src: 'auto', at: '2026-07' },
    station:      { v: '城ヶ崎海岸 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "243": {  /* Azure Palace 伊豆高原 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 329, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 41分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "244": {  /* HAKU-AKAZAWA- 【波空】 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 6, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 41分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆大川 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "245": {  /* villa 緑と物語 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 128, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 44分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆高原 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 2, src: 'auto', at: '2026-07' }
  },

  "246": {  /* SANU 2nd Home 伊豆1st */
    sauna_exists:    { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.sa-nu.com/list/raym_izu1st' },
    kitchen_type:    { v: 'ih', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    kitchen_burners: { v: 3, src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    capacity:        { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:       { v: 21, src: 'auto', at: '2026-07' },
    supermarket:     { v: 2, src: 'auto', at: '2026-07' },
    conveni:         { v: 5, src: 'auto', at: '2026-07' },
    ic:              { v: '山伏峠IC 45分', src: 'auto', at: '2026-07' },
    station:         { v: '富戸 2分', src: 'auto', at: '2026-07' },
    onsen:           { v: 2, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://2ndhome.sa-nu.com/supplies_list_new/sanucabin' }
  },

  "247": {  /* SANA 伊豆大室山-Pool Villa- */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 285, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 41分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "248": {  /* エンゼルフォレスト中伊豆 */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://reserve.489ban.net/client/ang-n/0/plan/room/37807' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 445, src: 'auto', at: '2026-07' },
    supermarket:  { v: 24, src: 'auto', at: '2026-07' },
    conveni:      { v: 14, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '伊東 24分', src: 'auto', at: '2026-07' },
    onsen:        { v: 15, src: 'auto', at: '2026-07' }
  },

  "249": {  /* グラン熱川 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 276, src: 'auto', at: '2026-07' },
    supermarket:  { v: 8, src: 'auto', at: '2026-07' },
    conveni:      { v: 7, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 40分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆熱川 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "250": {  /* プライベートリゾート南風 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 252, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 42分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆熱川 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "251": {  /* LAMERVON */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 10, src: 'desk', at: '2026-07' },
    elevation:    { v: 223, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 42分', src: 'auto', at: '2026-07' },
    station:      { v: '城ヶ崎海岸 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "252": {  /* 伊豆高原テントリゾート */
    capacity:    { v: 6, src: 'desk', at: '2026-07' },
    elevation:   { v: 275, src: 'auto', at: '2026-07' },
    supermarket: { v: 7, src: 'auto', at: '2026-07' },
    conveni:     { v: 8, src: 'auto', at: '2026-07' },
    ic:          { v: '大平IC 40分', src: 'auto', at: '2026-07' },
    station:     { v: '伊豆高原 9分', src: 'auto', at: '2026-07' },
    onsen:       { v: 7, src: 'auto', at: '2026-07' }
  },

  "253": {  /* 伊豆グランピングリゾートIshiki385 */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://izuglam385.com/stay/' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 49, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 28分', src: 'auto', at: '2026-07' },
    station:      { v: '稲梓 25分', src: 'auto', at: '2026-07' },
    onsen:        { v: 4, src: 'auto', at: '2026-07' }
  },

  "254": {  /* 伊豆グランヴィレッジ　グランピング */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://travel.rakuten.co.jp/HOTEL/184404/184404.html' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 228, src: 'auto', at: '2026-07' },
    supermarket:  { v: 7, src: 'auto', at: '2026-07' },
    conveni:      { v: 4, src: 'auto', at: '2026-07' },
    ic:           { v: '大平IC 41分', src: 'auto', at: '2026-07' },
    station:      { v: '富戸 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "255": {  /* 貸別荘「碧 ai」 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'tent', src: 'desk', at: '2026-07' },
    capacity:     { v: 10, src: 'desk', at: '2026-07' },
    elevation:    { v: 1, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆急下田 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 14, src: 'auto', at: '2026-07' }
  },

  "256": {  /* パーパスリゾート EG Sky Terrace 熱川 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    capacity:     { v: 12, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 105, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 3, src: 'auto', at: '2026-07' },
    ic:           { v: '河津逆川IC 33分', src: 'auto', at: '2026-07' },
    station:      { v: '伊豆熱川 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "257": {  /* THE GLAMPING 箱根十国峠 */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.jukkoku-cable.jp/glamping/' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 756, src: 'auto', at: '2026-07' },
    supermarket:  { v: 14, src: 'auto', at: '2026-07' },
    conveni:      { v: 11, src: 'auto', at: '2026-07' },
    ic:           { v: '熱海峠IC 2分', src: 'auto', at: '2026-07' },
    station:      { v: '十国峠 4分', src: 'auto', at: '2026-07' },
    onsen:        { v: 27, src: 'auto', at: '2026-07' }
  },

  "258": {  /* ALIVIO LUXE */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 187, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '山伏峠IC 36分', src: 'auto', at: '2026-07' },
    station:      { v: '川奈 8分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "259": {  /* 赤城宿 清芳山荘 -seiho- */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-08', url: 'https://akagi-shuku.com/hotels/seiho-sanso/honkan/' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://akagi-shuku.com/hotels/seiho-sanso/honkan/' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    elevation:       { v: 528, src: 'auto', at: '2026-07' },
    supermarket:     { v: 4, src: 'auto', at: '2026-07' },
    conveni:         { v: 5, src: 'auto', at: '2026-07' },
    ic:              { v: '渋川伊香保IC 22分', src: 'auto', at: '2026-07' },
    station:         { v: '大胡 16分', src: 'auto', at: '2026-07' },
    onsen:           { v: 4, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://akagi-shuku.com/hotels/seiho-sanso/honkan/' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://akagi-shuku.com/hotels/seiho-sanso/honkan/' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://akagi-shuku.com/hotels/seiho-sanso/honkan/' },
    bring_wrap:      { v: 'ready', src: 'desk', at: '2026-08', url: 'https://akagi-shuku.com/hotels/seiho-sanso/honkan/' }
  },

  "260": {  /* 赤城宿 珠蕾山荘 -shurai- */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    steps:        { v: 'flat', src: 'desk', at: '2026-08', url: 'https://akagi-shuku.com/hotels/shurai-sanso/' },
    elevation:    { v: 557, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 6, src: 'auto', at: '2026-07' },
    ic:           { v: '渋川伊香保IC 23分', src: 'auto', at: '2026-07' },
    station:      { v: '大胡 17分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "261": {  /* Earthboat Minakami Fujiwara */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 840, src: 'auto', at: '2026-07' },
    supermarket:  { v: 33, src: 'auto', at: '2026-07' },
    conveni:      { v: 20, src: 'auto', at: '2026-07' },
    ic:           { v: '谷川岳PA(下り) 27分', src: 'auto', at: '2026-07' },
    station:      { v: '湯檜曽 17分', src: 'auto', at: '2026-07' },
    onsen:        { v: 6, src: 'auto', at: '2026-07' }
  },

  "262": {  /* Earthboat Minakami Hodaigi */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 3, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 958, src: 'auto', at: '2026-07' },
    supermarket:  { v: 34, src: 'auto', at: '2026-07' },
    conveni:      { v: 20, src: 'auto', at: '2026-07' },
    ic:           { v: '谷川岳PA(下り) 27分', src: 'auto', at: '2026-07' },
    station:      { v: '湯檜曽 17分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "263": {  /* アウトドア貸切別荘北軽井沢1 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-1/' },
    bbq_roof:     { v: 'roof', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-1/' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-1/' },
    capacity:     { v: 7, src: 'desk', at: '2026-07' },
    comfort_cap:  { v: 7, src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-1/' },
    pet_ok:       { v: 'no', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-1/' },
    elevation:    { v: 976, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '厚田IC 37分', src: 'auto', at: '2026-07' },
    station:      { v: '万座・鹿沢口 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' },
    firewood_fee: { v: 'extra', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-1/' }
  },

  "264": {  /* アウトドア貸切別荘北軽井沢2 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    bbq_roof:     { v: 'roof', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-2/' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-2/' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    comfort_cap:  { v: 4, src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-2/' },
    pet_ok:       { v: 'no', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-2/' },
    elevation:    { v: 1102, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 7, src: 'auto', at: '2026-07' },
    ic:           { v: '小諸IC 47分', src: 'auto', at: '2026-07' },
    station:      { v: '大前 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 11, src: 'auto', at: '2026-07' },
    firewood_fee: { v: 'extra', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-cottage-kitakaruizawa-2/' }
  },

  "265": {  /* アウトドアアトラクション北軽井沢 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    bbq_roof:     { v: 'roof', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-attraction-kitakaruizawa/' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-attraction-kitakaruizawa/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    comfort_cap:  { v: 6, src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-attraction-kitakaruizawa/' },
    pet_ok:       { v: 'no', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-attraction-kitakaruizawa/' },
    elevation:    { v: 981, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 10, src: 'auto', at: '2026-07' },
    ic:           { v: '厚田IC 38分', src: 'auto', at: '2026-07' },
    station:      { v: '万座・鹿沢口 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' },
    firewood_fee: { v: 'extra', src: 'desk', at: '2026-08', url: 'https://www.kashikiribesso.com/outdoor-attraction-kitakaruizawa/' }
  },

  "266": {  /* 温泉グランピングシマブルー */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://shimablue.jp' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 674, src: 'auto', at: '2026-07' },
    supermarket:  { v: 23, src: 'auto', at: '2026-07' },
    conveni:      { v: 24, src: 'auto', at: '2026-07' },
    ic:           { v: '厚田IC 29分', src: 'auto', at: '2026-07' },
    station:      { v: '中之条 25分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "267": {  /* MOOSKA DE STUBEN */
    sauna_exists:    { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:      { v: 'hut', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    stove:           { v: 'wood', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    sauna_cap:       { v: 8, src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    loyly:           { v: 'yes', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    coldbath:        { v: 'bath', src: 'desk', at: '2026-07' },
    water_src:       { v: 'spring', src: 'desk', at: '2026-08', url: 'https://mooska.jp/sauna' },
    outdoor_rest:    { v: 'yes', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    villa_type:      { v: 'solo', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    firepit:         { v: 'stand', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    capacity:        { v: 8, src: 'desk', at: '2026-07' },
    pet_ok:          { v: 'yes', src: 'desk', at: '2026-07' },
    steps:           { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    wifi:            { v: 'yes', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    elevation:       { v: 483, src: 'auto', at: '2026-07' },
    supermarket:     { v: 10, src: 'auto', at: '2026-07' },
    conveni:         { v: 2, src: 'auto', at: '2026-07' },
    ic:              { v: '下牧PA(上り) 9分', src: 'auto', at: '2026-07' },
    station:         { v: '上牧 1分', src: 'auto', at: '2026-07' },
    onsen:           { v: 2, src: 'auto', at: '2026-07' },
    bring_amenity:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    bring_seasoning: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    bring_towel:     { v: 'ready', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    early_late:      { v: 'yes', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    fee_bbq:         { v: 'extra', src: 'desk', at: '2026-08', url: 'https://mooska.jp' },
    late_arrival:    { v: 'no', src: 'desk', at: '2026-08', url: 'https://mooska.jp' }
  },

  "268": {  /* ポーラーハウス南軽井沢1 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    villa_type:   { v: 'solo', src: 'desk', at: '2026-08', url: 'https://www.polar-resort.com/建物別詳細予約' },
    bbq_roof:     { v: 'open', src: 'desk', at: '2026-08', url: 'https://www.polar-resort.com/建物別詳細予約' },
    capacity:     { v: 15, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-08', url: 'https://www.polar-resort.com/建物別詳細予約' },
    elevation:    { v: 939, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 8, src: 'auto', at: '2026-07' },
    ic:           { v: '横川SA(上り) 13分', src: 'auto', at: '2026-07' },
    station:      { v: '軽井沢 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "269": {  /* THE LOOKOUT KUSATSU */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 8, src: 'desk', at: '2026-07' },
    elevation:    { v: 1134, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '厚田IC 34分', src: 'auto', at: '2026-07' },
    station:      { v: '羽根尾 12分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "270": {  /* COCO VILLA 長瀞 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    elevation:    { v: 241, src: 'auto', at: '2026-07' },
    supermarket:  { v: 2, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '寄居折原 8分', src: 'auto', at: '2026-07' },
    station:      { v: '樋口 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "271": {  /* Earthboat Saitama Kawajima */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    firepit:      { v: 'stand', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 12, src: 'auto', at: '2026-07' },
    supermarket:  { v: 9, src: 'auto', at: '2026-07' },
    conveni:      { v: 5, src: 'auto', at: '2026-07' },
    ic:           { v: '桶川北本IC 11分', src: 'auto', at: '2026-07' },
    station:      { v: '鴻巣 13分', src: 'auto', at: '2026-07' },
    onsen:        { v: 12, src: 'auto', at: '2026-07' }
  },

  "272": {  /* ノーラ名栗 */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://travel.rakuten.co.jp/HOTEL/188834/188834.html' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 250, src: 'auto', at: '2026-07' },
    supermarket:  { v: 18, src: 'auto', at: '2026-07' },
    conveni:      { v: 19, src: 'auto', at: '2026-07' },
    ic:           { v: '狭山PA(外廻り) 46分', src: 'auto', at: '2026-07' },
    station:      { v: '西吾野 18分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "273": {  /* HOLE37 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 53, src: 'auto', at: '2026-07' },
    supermarket:  { v: 6, src: 'auto', at: '2026-07' },
    conveni:      { v: 6, src: 'auto', at: '2026-07' },
    ic:           { v: '千代田PA(下り) 23分', src: 'auto', at: '2026-07' },
    station:      { v: '宮脇 16分', src: 'auto', at: '2026-07' },
    onsen:        { v: 13, src: 'auto', at: '2026-07' }
  },

  "274": {  /* サンライズヴィラ大洗 */
    sauna_exists:  { v: 'shared', src: 'desk', at: '2026-08', url: 'https://sunrise-villa.jp/facility/' },
    stove:         { v: 'electric', src: 'desk', at: '2026-07' },
    sauna_hours:   { v: 'limited', src: 'desk', at: '2026-08', url: 'https://sunrise-villa.jp/facility/' },
    villa_type:    { v: 'multi', src: 'desk', at: '2026-08', url: 'https://sunrise-villa.jp/private-use/' },
    bbq_roof:      { v: 'roof', src: 'desk', at: '2026-08', url: 'https://sunrise-villa.jp/guest-room/' },
    capacity:      { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:        { v: 'yes', src: 'desk', at: '2026-07' },
    steps:         { v: 'stairs', src: 'desk', at: '2026-08', url: 'https://sunrise-villa.jp/guest-room/' },
    elevation:     { v: 7, src: 'auto', at: '2026-07' },
    supermarket:   { v: 5, src: 'auto', at: '2026-07' },
    conveni:       { v: 3, src: 'auto', at: '2026-07' },
    ic:            { v: '夏海IC 1分', src: 'auto', at: '2026-07' },
    station:       { v: '大洗 5分', src: 'auto', at: '2026-07' },
    onsen:         { v: 2, src: 'auto', at: '2026-07' },
    bring_amenity: { v: 'ready', src: 'desk', at: '2026-08', url: 'https://sunrise-villa.jp/guest-room/' },
    bring_towel:   { v: 'ready', src: 'desk', at: '2026-08', url: 'https://sunrise-villa.jp/guest-room/' }
  },

  "275": {  /* ときわ邸 M-GARDEN */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 25, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '水戸北スマートIC 19分', src: 'auto', at: '2026-07' },
    station:      { v: '偕楽園 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  },

  "276": {  /* COCO VILLA 大洗 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'electric', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    rest_chair:   { v: 'chair', src: 'desk', at: '2026-07' },
    capacity:     { v: 9, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 19, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '夏海IC 6分', src: 'auto', at: '2026-07' },
    station:      { v: '涸沼 9分', src: 'auto', at: '2026-07' },
    onsen:        { v: 8, src: 'auto', at: '2026-07' }
  },

  "277": {  /* No.12 Kashima Fan Zone */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    sauna_type:   { v: 'barrel', src: 'desk', at: '2026-07' },
    coldbath:     { v: 'bath', src: 'desk', at: '2026-07' },
    chiller:      { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 38, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '潮来IC 11分', src: 'auto', at: '2026-07' },
    station:      { v: '鹿島サッカースタジアム 2分', src: 'auto', at: '2026-07' },
    onsen:        { v: 9, src: 'auto', at: '2026-07' }
  },

  "278": {  /* LUCY RESORT（ルーシー リゾート） */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.lucyresort.com/glamping/enjoy/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 25, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: 'つくば西スマートIC 6分', src: 'auto', at: '2026-07' },
    station:      { v: '万博記念公園 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 7, src: 'auto', at: '2026-07' }
  },

  "279": {  /* 大谷石の蔵サウナと古民家宿 DAIGO SAUNA */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    stove:        { v: 'wood', src: 'desk', at: '2026-07' },
    outdoor_rest: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 14, src: 'desk', at: '2026-07' },
    elevation:    { v: 127, src: 'auto', at: '2026-07' },
    supermarket:  { v: 4, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '中郷SA(下り) 53分', src: 'auto', at: '2026-07' },
    station:      { v: '常陸大子 1分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "280": {  /* 一棟貸切宿　藤右衛門 */
    sauna_exists: { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 5, src: 'auto', at: '2026-07' },
    supermarket:  { v: 10, src: 'auto', at: '2026-07' },
    conveni:      { v: 9, src: 'auto', at: '2026-07' },
    ic:           { v: '千代田石岡IC 23分', src: 'auto', at: '2026-07' },
    station:      { v: '高浜 12分', src: 'auto', at: '2026-07' },
    onsen:        { v: 18, src: 'auto', at: '2026-07' }
  },

  "281": {  /* SPA＆ごはんゆるうむ */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://yuluumu.co.jp/' },
    loyly:        { v: 'yes', src: 'desk', at: '2026-07' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    elevation:    { v: 30, src: 'auto', at: '2026-07' },
    supermarket:  { v: 1, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '茨城町JCT 11分', src: 'auto', at: '2026-07' },
    station:      { v: '偕楽園 10分', src: 'auto', at: '2026-07' },
    onsen:        { v: 1, src: 'auto', at: '2026-07' }
  },

  "282": {  /* GLAMPING KASHIMA 753 #00 */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://gp753.jp/kashima/%E3%83%90%E3%83%AC%E3%83%AB%E3%82%B5%E3%82%A6%E3%83%8A/' },
    capacity:     { v: 5, src: 'desk', at: '2026-07' },
    elevation:    { v: 28, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '潮来行方IC 16分', src: 'auto', at: '2026-07' },
    station:      { v: '鹿島大野 3分', src: 'auto', at: '2026-07' },
    onsen:        { v: 3, src: 'auto', at: '2026-07' }
  },

  "283": {  /* THE BOTANICAL RESORT 林音（リンネ） */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://rinne-resort.jp/rinnenoyu' },
    capacity:     { v: 4, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 52, src: 'auto', at: '2026-07' },
    supermarket:  { v: 5, src: 'auto', at: '2026-07' },
    conveni:      { v: 1, src: 'auto', at: '2026-07' },
    ic:           { v: '水戸北スマートIC 13分', src: 'auto', at: '2026-07' },
    station:      { v: '常陸鴻巣 5分', src: 'auto', at: '2026-07' },
    onsen:        { v: 18, src: 'auto', at: '2026-07' }
  },

  "284": {  /* ALOHA GLAMPING RESORT SAKAI */
    sauna_exists: { v: 'shared', src: 'desk', at: '2026-08', url: 'https://www.ibaraki-sakai-glamping.com/' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    elevation:    { v: 17, src: 'auto', at: '2026-07' },
    supermarket:  { v: 3, src: 'auto', at: '2026-07' },
    conveni:      { v: 2, src: 'auto', at: '2026-07' },
    ic:           { v: '五霞IC 10分', src: 'auto', at: '2026-07' },
    station:      { v: '南栗橋 17分', src: 'auto', at: '2026-07' },
    onsen:        { v: 5, src: 'auto', at: '2026-07' }
  },

  "285": {  /* 上小川レジャーペンション */
    sauna_exists: { v: 'room', src: 'desk', at: '2026-08', url: 'https://www.cottagelife.jp/ibaraki/la100200/id5473.html' },
    capacity:     { v: 6, src: 'desk', at: '2026-07' },
    pet_ok:       { v: 'yes', src: 'desk', at: '2026-07' },
    elevation:    { v: 73, src: 'auto', at: '2026-07' },
    supermarket:  { v: 18, src: 'auto', at: '2026-07' },
    conveni:      { v: 6, src: 'auto', at: '2026-07' },
    ic:           { v: '日立中央IC 66分', src: 'auto', at: '2026-07' },
    station:      { v: '上小川 7分', src: 'auto', at: '2026-07' },
    onsen:        { v: 10, src: 'auto', at: '2026-07' }
  }
};
