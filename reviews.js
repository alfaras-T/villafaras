(function () {
  var FIREBASE_PROJECT_ID = 'villafaras-reviews';
  var FIREBASE_API_KEY = 'AIzaSyAZGDB6MpEMBIF8-vMdX5wl8GcMoxODMAQ';
  var FIRESTORE_BASE = 'https://firestore.googleapis.com/v1/projects/' + FIREBASE_PROJECT_ID + '/databases/(default)/documents';

  function xhrRequest(method, url, body, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (xhr.status >= 200 && xhr.status < 300) {
          var data = null;
          try {
            data = JSON.parse(xhr.responseText);
          } catch (e) {}
          callback(null, data);
        } else {
          callback(new Error('HTTP ' + xhr.status + ': ' + xhr.responseText), null);
        }
      }
    };
    xhr.send(body ? JSON.stringify(body) : null);
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function formatDate(isoString) {
    if (!isoString) return '';
    var d = new Date(isoString);
    if (isNaN(d.getTime())) return '';
    return d.getFullYear() + '\u5e74' + (d.getMonth() + 1) + '\u6708' + d.getDate() + '\u65e5';
  }

  function renderStars(rating) {
    var full = Math.round(rating);
    var html = '';
    for (var i = 1; i <= 5; i++) {
      html += i <= full ? '\u2605' : '\u2606';
    }
    return html;
  }

  function fetchReviews(villaId, onDone) {
    var url = FIRESTORE_BASE + ':runQuery?key=' + FIREBASE_API_KEY;
    var body = {
      structuredQuery: {
        from: [{ collectionId: 'reviews' }],
        where: {
          compositeFilter: {
            op: 'AND',
            filters: [
              { fieldFilter: { field: { fieldPath: 'villaId' }, op: 'EQUAL', value: { stringValue: villaId } } },
              { fieldFilter: { field: { fieldPath: 'approved' }, op: 'EQUAL', value: { booleanValue: true } } }
            ]
          }
        },
        orderBy: [{ field: { fieldPath: 'createdAt' }, direction: 'DESCENDING' }]
      }
    };
    xhrRequest('POST', url, body, function (err, data) {
      if (err || !data) {
        onDone(err, []);
        return;
      }
      var reviews = [];
      for (var i = 0; i < data.length; i++) {
        var doc = data[i].document;
        if (!doc || !doc.fields) continue;
        var f = doc.fields;
        reviews.push({
          name: f.name && f.name.stringValue ? f.name.stringValue : '\u533f\u540d',
          rating: f.rating && f.rating.integerValue ? parseInt(f.rating.integerValue, 10) : 0,
          comment: f.comment && f.comment.stringValue ? f.comment.stringValue : '',
          createdAt: f.createdAt && f.createdAt.timestampValue ? f.createdAt.timestampValue : ''
        });
      }
      onDone(null, reviews);
    });
  }

  function submitReview(villaId, name, rating, comment, onDone) {
    var url = FIRESTORE_BASE + '/reviews?key=' + FIREBASE_API_KEY;
    var body = {
      fields: {
        villaId: { stringValue: villaId },
        name: { stringValue: name || '\u533f\u540d' },
        rating: { integerValue: String(rating) },
        comment: { stringValue: comment },
        approved: { booleanValue: false },
        createdAt: { timestampValue: new Date().toISOString() }
      }
    };
    xhrRequest('POST', url, body, onDone);
  }

  var ratingsState = { data: {}, ready: false, loading: false, callbacks: [] };

  function loadAllRatings(cb) {
    if (ratingsState.ready) {
      cb(ratingsState.data);
      return;
    }
    ratingsState.callbacks.push(cb);
    if (ratingsState.loading) return;
    ratingsState.loading = true;

    var url = FIRESTORE_BASE + ':runQuery?key=' + FIREBASE_API_KEY;
    var body = {
      structuredQuery: {
        from: [{ collectionId: 'reviews' }],
        where: {
          fieldFilter: { field: { fieldPath: 'approved' }, op: 'EQUAL', value: { booleanValue: true } }
        }
      }
    };
    xhrRequest('POST', url, body, function (err, data) {
      var totals = {};
      if (!err && data) {
        for (var i = 0; i < data.length; i++) {
          var doc = data[i].document;
          if (!doc || !doc.fields) continue;
          var f = doc.fields;
          var vid = f.villaId && f.villaId.stringValue ? f.villaId.stringValue : null;
          var rating = f.rating && f.rating.integerValue ? parseInt(f.rating.integerValue, 10) : 0;
          if (!vid) continue;
          if (!totals[vid]) totals[vid] = { total: 0, count: 0 };
          totals[vid].total += rating;
          totals[vid].count += 1;
        }
      }
      var finalMap = {};
      for (var k in totals) {
        if (!totals.hasOwnProperty(k)) continue;
        finalMap[k] = { avg: totals[k].total / totals[k].count, count: totals[k].count };
      }
      ratingsState.data = finalMap;
      ratingsState.ready = true;
      ratingsState.loading = false;
      var cbs = ratingsState.callbacks;
      ratingsState.callbacks = [];
      for (var j = 0; j < cbs.length; j++) {
        cbs[j](finalMap);
      }
    });
  }

  window.villafarasApplyCardRatings = function () {
    loadAllRatings(function (map) {
      var els = document.querySelectorAll('[data-rating-for]');
      for (var i = 0; i < els.length; i++) {
        var el = els[i];
        var vid = el.getAttribute('data-rating-for');
        var info = map[vid];
        if (info) {
          el.innerHTML =
            '<span class="card-rating-stars">' + renderStars(info.avg) + '</span>' +
            '<span class="card-rating-num">' + info.avg.toFixed(1) + '</span>' +
            '<span class="card-rating-count">(' + info.count + ')</span>';
          el.style.display = 'flex';
        } else {
          el.innerHTML = '';
          el.style.display = 'none';
        }
      }
    });
  };

  function initReviewWidget(container) {
    var villaId = container.getAttribute('data-villa-id');
    if (!villaId) return;

    var summaryEl = document.createElement('div');
    summaryEl.className = 'review-summary';

    var listEl = document.createElement('div');
    listEl.className = 'review-list';
    listEl.innerHTML = '<div class="review-loading">\u53e3\u30b3\u30df\u3092\u8aad\u307f\u8fbc\u307f\u4e2d...</div>';

    var formWrap = document.createElement('div');
    formWrap.className = 'review-form-wrap';
    formWrap.innerHTML =
      '<h3 class="review-form-title">\u53e3\u30b3\u30df\u3092\u6295\u7a3f\u3059\u308b</h3>' +
      '<div class="review-form-row">' +
        '<label>\u304a\u540d\u524d\uff08\u4efb\u610f\uff09</label>' +
        '<input type="text" class="review-input-name" maxlength="30" placeholder="\u30cb\u30c3\u30af\u30cd\u30fc\u30e0\u3067\u3082OK">' +
      '</div>' +
      '<div class="review-form-row">' +
        '<label>\u8a55\u4fa1</label>' +
        '<select class="review-input-rating">' +
          '<option value="5">\u2605\u2605\u2605\u2605\u2605 (5)</option>' +
          '<option value="4">\u2605\u2605\u2605\u2605\u2606 (4)</option>' +
          '<option value="3">\u2605\u2605\u2605\u2606\u2606 (3)</option>' +
          '<option value="2">\u2605\u2605\u2606\u2606\u2606 (2)</option>' +
          '<option value="1">\u2605\u2606\u2606\u2606\u2606 (1)</option>' +
        '</select>' +
      '</div>' +
      '<div class="review-form-row">' +
        '<label>\u30b3\u30e1\u30f3\u30c8</label>' +
        '<textarea class="review-input-comment" maxlength="500" rows="4" placeholder="\u5bbf\u6cca\u3057\u305f\u611f\u60f3\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044"></textarea>' +
      '</div>' +
      '<button type="button" class="review-submit-btn">\u6295\u7a3f\u3059\u308b</button>' +
      '<div class="review-form-msg"></div>';

    container.appendChild(summaryEl);
    container.appendChild(listEl);
    container.appendChild(formWrap);

    function loadAndRender() {
      fetchReviews(villaId, function (err, reviews) {
        if (err) {
          listEl.innerHTML = '<div class="review-empty">\u53e3\u30b3\u30df\u306e\u8aad\u307f\u8fbc\u307f\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002</div>';
          summaryEl.innerHTML = '';
          return;
        }
        if (reviews.length === 0) {
          summaryEl.innerHTML = '';
          listEl.innerHTML = '<div class="review-empty">\u307e\u3060\u53e3\u30b3\u30df\u304c\u3042\u308a\u307e\u305b\u3093\u3002\u6700\u521d\u306e\u53e3\u30b3\u30df\u3092\u6295\u7a3f\u3057\u3066\u307f\u307e\u305b\u3093\u304b\uff1f</div>';
          return;
        }
        var total = 0;
        for (var i = 0; i < reviews.length; i++) {
          total += reviews[i].rating;
        }
        var avg = total / reviews.length;
        summaryEl.innerHTML =
          '<span class="review-avg-stars">' + renderStars(avg) + '</span>' +
          '<span class="review-avg-num">' + avg.toFixed(1) + '</span>' +
          '<span class="review-count">(' + reviews.length + '\u4ef6\u306e\u53e3\u30b3\u30df)</span>';

        var html = '';
        for (var j = 0; j < reviews.length; j++) {
          var r = reviews[j];
          html +=
            '<div class="review-item">' +
              '<div class="review-item-head">' +
                '<span class="review-item-stars">' + renderStars(r.rating) + '</span>' +
                '<span class="review-item-name">' + escapeHtml(r.name) + '</span>' +
                '<span class="review-item-date">' + formatDate(r.createdAt) + '</span>' +
              '</div>' +
              '<div class="review-item-comment">' + escapeHtml(r.comment).replace(/\n/g, '<br>') + '</div>' +
            '</div>';
        }
        listEl.innerHTML = html;
      });
    }

    var submitBtn = formWrap.querySelector('.review-submit-btn');
    var msgEl = formWrap.querySelector('.review-form-msg');

    submitBtn.addEventListener('click', function () {
      var name = formWrap.querySelector('.review-input-name').value.replace(/^\s+|\s+$/g, '');
      var rating = parseInt(formWrap.querySelector('.review-input-rating').value, 10);
      var comment = formWrap.querySelector('.review-input-comment').value.replace(/^\s+|\s+$/g, '');

      if (!comment) {
        msgEl.textContent = '\u30b3\u30e1\u30f3\u30c8\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044\u3002';
        msgEl.className = 'review-form-msg review-form-msg-error';
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = '\u9001\u4fe1\u4e2d...';

      submitReview(villaId, name, rating, comment, function (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = '\u6295\u7a3f\u3059\u308b';
        if (err) {
          msgEl.textContent = '\u9001\u4fe1\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002\u6642\u9593\u3092\u304a\u3044\u3066\u518d\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002';
          msgEl.className = 'review-form-msg review-form-msg-error';
          return;
        }
        msgEl.textContent = '\u3054\u6295\u7a3f\u3042\u308a\u304c\u3068\u3046\u3054\u3056\u3044\u307e\u3059\uff01\u78ba\u8a8d\u5f8c\u306b\u63b2\u8f09\u3055\u308c\u307e\u3059\u3002';
        msgEl.className = 'review-form-msg review-form-msg-success';
        formWrap.querySelector('.review-input-name').value = '';
        formWrap.querySelector('.review-input-comment').value = '';
      });
    });

    loadAndRender();
  }

  function init() {
    var containers = document.querySelectorAll('.review-widget');
    for (var i = 0; i < containers.length; i++) {
      if (containers[i].getAttribute('data-review-inited') === '1') continue;
      containers[i].setAttribute('data-review-inited', '1');
      initReviewWidget(containers[i]);
    }
    if (document.querySelectorAll('[data-rating-for]').length > 0) {
      window.villafarasApplyCardRatings();
    }
  }

  window.villafarasInitReviews = init;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
