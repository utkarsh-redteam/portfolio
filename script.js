// Hero name typing effect is CSS-only (.hero-name .typed in style.css) so the <h1> text stays static.

// ---- Mobile nav toggle ----
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

if (navToggle && navLinks){
  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
  });

  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });
}

// ---- Active nav link on scroll ----
const sections = Array.from(document.querySelectorAll('section[id]'));
const navAnchors = Array.from(document.querySelectorAll('.nav-link'));

function setActiveLink(id){
  navAnchors.forEach(a => {
    const href = a.getAttribute('href');
    const isSectionLink = href && href.startsWith('#');
    a.classList.toggle('active', isSectionLink && href === '#' + id);
  });
}

function onScroll(){
  const headerHeight = document.querySelector('.nav')?.offsetHeight || 90;
  let current = '';
  let closestDistance = Infinity;

  sections.forEach(section => {
    const rect = section.getBoundingClientRect();
    const distance = Math.abs(rect.top - headerHeight);

    if (distance < closestDistance) {
      closestDistance = distance;
      current = section.getAttribute('id');
    }
  });

  setActiveLink(current);
}

navAnchors.forEach(a => {
  const href = a.getAttribute('href');
  if (href && href.startsWith('#')) {
    a.addEventListener('click', () => setActiveLink(href.slice(1)));
  }
});

window.addEventListener('scroll', onScroll, { passive: true });
window.addEventListener('resize', onScroll);
onScroll();

// ---- Footer year ----
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// ---- Lightbox for certificates page ----
document.addEventListener('DOMContentLoaded', () => {
  const thumbs = document.querySelectorAll('.cert-thumb');
  const lightbox = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightboxImg');
  const lbClose = document.getElementById('lightboxClose');
  const lbDownload = document.getElementById('lightboxDownload');

  if (!thumbs || thumbs.length === 0 || !lightbox) return;

  // Set role for accessibility
  lightbox.setAttribute('role', 'dialog');
  lightbox.setAttribute('aria-label', 'Certificate preview');

  thumbs.forEach(t => {
    t.addEventListener('click', (e) => {
      const src = e.currentTarget.getAttribute('src');
      lbImg.src = src;
      lbDownload.href = src;
      lightbox.style.display = 'flex';
      if (lbClose) lbClose.focus();
    });
  });

  function closeLb(){
    lightbox.style.display = 'none';
    lbImg.src = '';
  }

  if (lbClose) lbClose.addEventListener('click', closeLb);
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLb();
  });

  // Escape key to close lightbox
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && lightbox.style.display !== 'none') closeLb();
  });
});
