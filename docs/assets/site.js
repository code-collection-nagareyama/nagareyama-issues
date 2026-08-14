
(function(){
  var grid = document.getElementById('grid');
  if(!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
  var count = document.getElementById('count');
  var active = new Set();
  var sort = 'id';

  function apply(){
    var shown = 0;
    cards.forEach(function(c){
      var ok = active.size === 0 || active.has(c.dataset.theme);
      c.style.display = ok ? '' : 'none';
      if(ok) shown++;
    });
    if(count) count.textContent = shown;
    var key = {
      id:   function(c){ return parseInt(c.querySelector('.card-id').textContent.replace('N-',''),10); },
      data: function(c){ return -parseInt(c.dataset.data,10); },
      easy: function(c){ return parseInt(c.dataset.diff,10); }
    }[sort];
    cards.slice().sort(function(a,b){
      var d = key(a) - key(b);
      return d !== 0 ? d : a.querySelector('.card-id').textContent.localeCompare(b.querySelector('.card-id').textContent);
    }).forEach(function(c){ grid.appendChild(c); });
  }

  document.querySelectorAll('.chip[data-theme]').forEach(function(b){
    b.addEventListener('click', function(){
      var t = b.dataset.theme;
      if(active.has(t)){ active.delete(t); b.classList.remove('on'); }
      else { active.add(t); b.classList.add('on'); }
      apply();
    });
  });
  document.querySelectorAll('.chip.sort').forEach(function(b){
    b.addEventListener('click', function(){
      document.querySelectorAll('.chip.sort').forEach(function(x){ x.classList.remove('on'); });
      b.classList.add('on');
      sort = b.dataset.sort;
      apply();
    });
  });
  apply();
})();
