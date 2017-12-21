// This code snippet will ensure you can update test questions in the user interface without any issues.
var showGold = function() {
    var data = $$('form').retrieve('gold')[0].options.unitData;
    $$('.checkboxes').each(function(cb) {
        cb.getElements('input').each(function(input) {
            var answers = data[input.get('class').split(" ")[0]];
            if ((answers == input.value) || (Array.isArray(answers) && answers.contains(input.value))) {
                input.checked = true;
                input.fireEvent('change');
            }
        })
    })
}
if (_cf_cml.digging_gold) {
    showGold.delay(100)
}

//This code finds all the texts with class "full_text" and all the key words (deliminated by ',') in the class "quote_text". These key words can be dynamic meaning different words applicable to each unit full text. It replaces the words it finds with the word in a span that you can color with class: hightlight.
function highlight() {
    var full_text = document.getElementsByClassName("full_text");
    for (i = 0; i < full_text.length; i++) {
        var quote = document.getElementsByClassName("quote_text")[i].innerText;
        var quote_array = quote.split(",");
        for (j = 0; j < quote_array.length; j++) {
            reg_str = "<span.*?</span>|(\\b" + quote_array[j] + "\\b)";
            var regex2 = new RegExp(reg_str, "gi");
            var new_text = full_text[i].innerHTML.replace(regex2, function(m, group1) {
                if (group1 == null) return m;
                else return "<span class=\"highlight\">" + quote_array[j] + "</span>";
            });
            document.getElementsByClassName("full_text")[i].innerHTML = new_text;

            /*var replace_with = "<span class=\"" + "highlight" + "\">" + quote_array[j] + "</span>";
            var new_text = full_text[i].innerHTML.replace(new RegExp(quote_array[j], 'gi'), replace_with);*/
        }
    }
}

window.onload = highlight();
//