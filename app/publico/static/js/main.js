// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('theme-toggle');
  const body = document.body;

  // Carrega tema salvo
  if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-mode');
    toggle.innerHTML = '<i class="fas fa-sun"></i>';
  }

  // Alterna tema
  toggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');

    if (body.classList.contains('dark-mode')) {
      toggle.innerHTML = '<i class="fas fa-sun"></i>';
      localStorage.setItem('theme', 'dark');
    } else {
      toggle.innerHTML = '<i class="fas fa-moon"></i>';
      localStorage.setItem('theme', 'light');
    }
  });
});
