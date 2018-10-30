(() => {
  var now = Date.now();
  setInterval(() => {
    var elapsed = ((Date.now() - now)/1000)|0;
    var elements = document.getElementsByClassName('countdown');
    for (var i=0; i<elements.length; i++) {
      var element = elements[i];
      var seconds = element.getAttribute('data-time') - elapsed;
      if (seconds <= 0) {
        element.innerHTML = '&nbsp;';
        continue;
      }
      var days = (seconds / 86400)|0;
      var hours = ((seconds % 86400) / 3600)|0;
      var minutes = ((seconds % 3600) / 60)|0;
      var seconds = seconds % 60;

      if (days > 0) {
        element.textContent = days + ' day' + (days > 1 ? 's' : '') +
            ', ' + hours + ' hour' + (hours > 1 ? 's' : '');
      } else if (hours > 0) {
        element.textContent = hours + ' hour' + (hours > 1 ? 's' : '') +
            ', ' + minutes + ' minute' + (minutes > 1 ? 's' : '');
      } else if (minutes > 0) {
        element.textContent = minutes + ' minute' + (minutes > 1 ? 's' : '') +
            ', ' + seconds + ' second' + (seconds > 1 ? 's' : '');
      } else {
        element.textContent = seconds + ' second' + (seconds > 1 ? 's' : '');
      }
    }
  }, 1000);
})()
