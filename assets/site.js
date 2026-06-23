const topButton = document.getElementById('top');
const header = document.querySelector('.top');
const menu = document.querySelector('.menu-toggle');
window.addEventListener('scroll', () => {
  if (!topButton) return;
  topButton.classList.toggle('show', window.scrollY > 500);
});
topButton?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
menu?.addEventListener('click', () => {
  const open = header.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
});
