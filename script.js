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

function sectionIdFromHref(href){
  if (!href) return null;
  if (href.startsWith('/#') && href.length > 2) return href.slice(2);
  if (href.startsWith('#') && href.length > 1 && !href.startsWith('#main')) return href.slice(1);
  return null;
}

function setActiveLink(id){
  navAnchors.forEach(a => {
    const sectionId = sectionIdFromHref(a.getAttribute('href'));
    if (!sectionId) return;
    a.classList.toggle('active', sectionId === id);
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
  const sectionId = sectionIdFromHref(a.getAttribute('href'));
  if (sectionId) {
    a.addEventListener('click', () => setActiveLink(sectionId));
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
  const triggers = document.querySelectorAll('.cert-open');
  const lightbox = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightboxImg');
  const lbClose = document.getElementById('lightboxClose');
  const lbDownload = document.getElementById('lightboxDownload');

  if (!triggers.length || !lightbox || !lbImg) return;

  let lastFocus = null;
  const focusableSelector = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';

  function backgroundNodes(){
    return Array.from(document.body.children).filter(el => el !== lightbox);
  }

  function setBackgroundHidden(hidden){
    backgroundNodes().forEach(el => {
      if (hidden) {
        if (!el.hasAttribute('data-aria-hidden')) {
          el.setAttribute('data-aria-hidden', el.getAttribute('aria-hidden') ?? '');
        }
        el.setAttribute('aria-hidden', 'true');
      } else if (el.hasAttribute('data-aria-hidden')) {
        const prev = el.getAttribute('data-aria-hidden');
        if (prev) el.setAttribute('aria-hidden', prev);
        else el.removeAttribute('aria-hidden');
        el.removeAttribute('data-aria-hidden');
      }
    });
  }

  function openLb(trigger){
    lastFocus = trigger;
    lightbox.hidden = false;
    setBackgroundHidden(true);
    document.body.style.overflow = 'hidden';
    if (lbClose) lbClose.focus();
  }

  function closeLb(){
    lightbox.hidden = true;
    lbImg.removeAttribute('src');
    setBackgroundHidden(false);
    document.body.style.overflow = '';
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  function trapTab(event){
    if (lightbox.hidden || event.key !== 'Tab') return;
    const nodes = Array.from(lightbox.querySelectorAll(focusableSelector));
    if (!nodes.length) return;
    const first = nodes[0];
    const last = nodes[nodes.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  triggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const img = trigger.querySelector('img');
      if (!img) return;
      const full = img.getAttribute('data-full') || img.getAttribute('src');
      lbImg.src = full;
      lbImg.alt = img.alt || 'Certificate';
      if (lbDownload) lbDownload.href = full;
      openLb(trigger);
    });
  });

  if (lbClose) lbClose.addEventListener('click', closeLb);
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) closeLb();
  });
  document.addEventListener('keydown', (event) => {
    if (lightbox.hidden) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      closeLb();
      return;
    }
    trapTab(event);
  });
});
