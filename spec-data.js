/* ==========================================================================
   villafaras 施設スペック データ
   --------------------------------------------------------------------------
   spec.js より先に読み込むこと。
   形式: VILLAFARAS_SPEC[villaId] = { fieldKey: { v: 値, src: 出典, at: 調査日, url: 出典URL } }

     src : 'owner'（施設回答） / 'desk'（公式サイト調べ） / 'auto'（座標算出） / 'review'（宿泊者）
     at  : 'YYYY-MM' 形式の調査日
     url : src が 'desk' の場合は出典URLを必ず記録する

   簡略記法として { fieldKey: '値' } も可。ただし出典バッジは表示されない。
   フィールドキーの一覧は spec.js の SCHEMA を参照。
   ========================================================================== */
window.VILLAFARAS_SPEC = {

  /* --- 既存データ移行分（5件） -------------------------------------------
     旧 index.html の saunaSpec から移行。出典が未記録のため暫定で 'desk' 扱い。
     オーナー確認済みのものがあれば src を 'owner' に変更すること。         */

  "54":  {  /* 絶景STAY ISUMI cabin */
    stove:   { v: 'wood', src: 'desk', at: '2026-07' },
    loyly:   { v: 'yes',  src: 'desk', at: '2026-07' }
  },

  "70":  {  /* The Pacific Retreat TATEYAMA */
    chiller: { v: 'yes',  src: 'desk', at: '2026-07' }
  },

  "116": {  /* Kito NASU */
    stove:   { v: 'wood', src: 'desk', at: '2026-07' }
  },

  "172": {  /* Oyado S */
    loyly:      { v: 'yes',    src: 'desk', at: '2026-07' },
    chiller:    { v: 'yes',    src: 'desk', at: '2026-07' },
    water_temp: { v: '10〜18', src: 'desk', at: '2026-07' }
  },

  "185": {  /* SAUNA VILLA 然 */
    loyly:   { v: 'yes',  src: 'desk', at: '2026-07' }
  }

  /* --- 以降、調査完了分をここに追記する ---------------------------------
     記入例:

     "12": {
       chiller:      { v: 'yes',    src: 'owner', at: '2026-08' },
       water_temp:   { v: 't1015',  src: 'owner', at: '2026-08' },
       bbq_roof:     { v: 'roof',   src: 'desk',  at: '2026-08',
                       url: 'https://example.jp/facility' },
       winter_access:{ v: 'tire',   src: 'auto',  at: '2026-08' },
       supermarket:  { v: 22,       src: 'auto',  at: '2026-08' }
     }
  ------------------------------------------------------------------------ */
};
