const url = new URL(window.location);
const page_now = url.searchParams.get('page');
function nextpage() {
    //const url = new URL(window.location);
    let page_num = parseInt(page_now) + 1;
    if (isNaN(page_num)) {
        page_num = 1;
    }
    window.location.href = '?page=' + page_num;
}

function previouspage() {
    //const url = new URL(window.location);
    let page_num = parseInt(page_now) - 1;
    if (page_num < 1 || isNaN(page_num)) {
        page_num = 1;
    }
    window.location.href = '?page=' + page_num;
}

// Добавьте активный класс к текущей кнопке (выделите его)
var header = document.getElementById("pages");
var btns = header.getElementsByClassName("page-item");


for (var i = 0; i < btns.length; i++) {
    let tag_a = btns[i].getElementsByTagName("a")['0'];
    if (tag_a.textContent===page_now){
        tag_a.className += " active_custom";
    }

  btns[i].addEventListener("click", function() {
    var current = document.getElementsByClassName("active_custom");
    current[0].className = current[0].className.replace(" active_custom", "");
    tag_a.className += " active_custom";
  });
}
