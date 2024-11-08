	var table = document.querySelector("table");
	var tr = table.querySelectorAll("tr");
	table.addEventListener("click", function(e) {
		if(e.target.tagName.toLowerCase() === "td") {
			//まずは全て背景色白
			for(var i = 0; i < tr.length; i++) {
				tr[i].style.backgroundColor = "#f5f8fa";
			}
			var col = e.target.parentNode.rowIndex;
			//選択行だけ色を変える
			e.target.parentNode.style.backgroundColor = "#eef";
		}
	}, false);