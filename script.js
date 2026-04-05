// HAMBURGER MENU
function toggleMenu() {
  const menu = document.querySelector(".menu-links");
  const icon = document.querySelector(".hamburger-icon");
  menu.classList.toggle("open");
  icon.classList.toggle("open");
}

// DARK MODE
function toggleTheme() {
  document.body.classList.toggle("dark-mode");
  const isDark = document.body.classList.contains("dark-mode");
  localStorage.setItem("theme", isDark ? "dark" : "light");
  document.querySelectorAll(".theme-icon").forEach(icon => {
    icon.innerHTML = isDark ? "&#9788;" : "&#9790;";
  });
}

// Load saved theme
(function() {
  const saved = localStorage.getItem("theme");
  if (saved === "dark") {
    document.body.classList.add("dark-mode");
    document.querySelectorAll(".theme-icon").forEach(icon => {
      icon.innerHTML = "&#9788;";
    });
  }
})();

// TYPING ANIMATION
const typingTexts = [
  "Data Analyst",
  "Python & SQL",
  "Turning Data into Insights",
  "BI & Dashboards",
  "ETL Pipelines"
];

let textIndex = 0;
let charIndex = 0;
let isDeleting = false;
const typingElement = document.querySelector(".typing-text");

function typeEffect() {
  if (!typingElement) return;

  const currentText = typingTexts[textIndex];

  if (isDeleting) {
    typingElement.textContent = currentText.substring(0, charIndex - 1);
    charIndex--;
  } else {
    typingElement.textContent = currentText.substring(0, charIndex + 1);
    charIndex++;
  }

  let speed = isDeleting ? 40 : 80;

  if (!isDeleting && charIndex === currentText.length) {
    speed = 2000;
    isDeleting = true;
  } else if (isDeleting && charIndex === 0) {
    isDeleting = false;
    textIndex = (textIndex + 1) % typingTexts.length;
    speed = 400;
  }

  setTimeout(typeEffect, speed);
}

document.addEventListener("DOMContentLoaded", function() {
  typeEffect();
});

// MODAL
function openModal(filePath) {
  const modal = document.getElementById("readmeModal");
  const readmeText = document.getElementById("readme-text");

  modal.style.display = "block";
  readmeText.innerHTML = "Loading README...";

  fetch(filePath)
    .then(response => {
      if (!response.ok) throw new Error("HTTP error! status: " + response.status);
      return response.text();
    })
    .then(data => {
      readmeText.innerHTML = marked.parse(data);
    })
    .catch(error => {
      readmeText.innerHTML = '<div style="text-align:center;padding:2rem;"><h3>Error loading README</h3><p style="color:#666;">' + error.message + '</p></div>';
    });
}

function closeModal() {
  document.getElementById("readmeModal").style.display = "none";
}

window.addEventListener("click", function(event) {
  if (event.target === document.getElementById("readmeModal")) closeModal();
});

document.addEventListener("keydown", function(event) {
  if (event.key === "Escape") closeModal();
});

// SMOOTH SCROLLING
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      const menu = document.querySelector(".menu-links");
      const icon = document.querySelector(".hamburger-icon");
      if (menu && menu.classList.contains("open")) {
        menu.classList.remove("open");
        icon.classList.remove("open");
      }
    }
  });
});

// SCROLL PROGRESS BAR
window.addEventListener("scroll", function() {
  const scrollProgress = document.querySelector(".scroll-progress");
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  scrollProgress.style.width = (scrollTop / scrollHeight) * 100 + "%";
});

// SCROLL REVEAL - sections fade in when visible
const observer = new IntersectionObserver(function(entries) {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");

      // Animate skill bars when skills section is visible
      if (entry.target.id === "experience") {
        document.querySelectorAll(".skill-fill").forEach(bar => {
          const width = bar.style.width;
          bar.style.width = "0%";
          setTimeout(() => { bar.style.width = width; }, 200);
        });
      }
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll("section").forEach(section => {
  if (section.id !== "profile") observer.observe(section);
});
