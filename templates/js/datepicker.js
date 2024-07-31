// デフォルト
const config = {
    'locale' : 'ja',
    allowInput : true,
    dateFormat : 'Y-m-d', 
  }
flatpickr('.flatpickr',config);

// 今日の日付を表示
const conftoday = {
    'locale' : 'ja',
    allowInput : true,
    defaultDate : 'today',
    dateFormat : 'Y-m-d', 
  }
flatpickr('.flatpickrtoday',conftoday);

// 年月を表示
const confformat = {
  'locale' : 'ja',
  allowInput : true,
  dateFormat: "Y年m月",
}
flatpickr('.flatpickrformat',confformat);