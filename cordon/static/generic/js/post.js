// ----- Convert url in text as link
function urlify(content) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;
    return content.replace(urlRegex, '<a target="new" href="$1">$1</a>')
    } // function
