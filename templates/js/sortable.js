document.addEventListener('DOMContentLoaded', function() {
  // ソート可能な列にイベントリスナーを設定
  document.querySelectorAll('#tblrow th[data-sort]').forEach(header => {
    header.addEventListener('click', function() {
      sortTable(this);
    });
  });

  // テーブルソート関数
  function sortTable(header) {
    const table = document.getElementById('tblrow');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    // 列のインデックスを取得
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);

    // データ型を取得
    const dataType = header.getAttribute('data-sort');

    // 現在のソート方向を取得
    const currentDir = header.getAttribute('data-sort-direction') || 'asc';
    const newDir = currentDir === 'asc' ? 'desc' : 'asc';

    // 他の列のソート状態をリセット
    document.querySelectorAll('#tblrow th').forEach(th => {
      th.removeAttribute('data-sort-direction');
    });

    // 現在の列のソート方向を設定
    header.setAttribute('data-sort-direction', newDir);

    // 行をソート
    rows.sort((rowA, rowB) => {
      let a = rowA.cells[columnIndex].textContent.trim();
      let b = rowB.cells[columnIndex].textContent.trim();

      // データ型に応じた比較
      if (dataType === 'number') {
        return (newDir === 'asc' ? 1 : -1) * (parseFloat(a) - parseFloat(b));
      } else if (dataType === 'date') {
        // 年月日を置き換え
        a = a.replace('年', '-');
        a = a.replace('月', '-');
        a = a.replace('日', '');
        // 年月日を置き換え
        b = b.replace('年', '-');
        b = b.replace('月', '-');
        b = b.replace('日', '');
        return (newDir === 'asc' ? 1 : -1) * (new Date(a) - new Date(b));
      } else {
        // 文字列比較（日本語対応）
        return (newDir === 'asc' ? 1 : -1) * a.localeCompare(b, 'ja');
      }
    });

    // ソートした行をテーブルに再配置
    rows.forEach(row => tbody.appendChild(row));
  }
});

