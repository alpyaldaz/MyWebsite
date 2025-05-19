function toggleMenu() {
  const menu = document.querySelector(".menu-links");
  const icon = document.querySelector(".hamburger-icon");
  menu.classList.toggle("open");
  icon.classList.toggle("open");
}

function openModal(filePath = './assests') {
  const modal = document.getElementById("readmeModal");
  const readmeText = document.getElementById("readme-text");
  
  modal.style.display = "block";
  readmeText.innerHTML = "Loading README...";
  
  fetch(filePath)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then(data => {
      readmeText.innerHTML = marked.parse(data);
    })
    .catch(error => {
      readmeText.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
          <h3>Error loading README</h3>
          <p style="color: #666;">${error.message}</p>
          <p>File path: ${filePath}</p>
        </div>
      `;
      console.error('Error loading README:', error);
    });
}

function closeModal() {
  const modal = document.getElementById("readmeModal");
  modal.style.display = "none";
}

// Close modal when clicking outside of it
window.addEventListener('click', function(event) {
  const modal = document.getElementById("readmeModal");
  if (event.target === modal) {
    closeModal();
  }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
  if (event.key === 'Escape') {
    closeModal();
  }
});

// Smooth scrolling for navigation links (additional enhancement)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
      
      // Close mobile menu if open
      const menu = document.querySelector(".menu-links");
      const icon = document.querySelector(".hamburger-icon");
      if (menu && menu.classList.contains('open')) {
        menu.classList.remove('open');
        icon.classList.remove('open');
      }
    }
  });
});

// Handle project clicks for better UX
document.addEventListener('DOMContentLoaded', function() {
  // Add click handlers for project titles and descriptions
  const projectTitles = document.querySelectorAll('.project-title');
  const projectDescriptions = document.querySelectorAll('.details-container p');
  
  projectTitles.forEach(title => {
    if (title.onclick) return; // Skip if onclick already defined
    
    title.style.cursor = 'pointer';
    title.addEventListener('mouseover', function() {
      this.style.color = '#666';
    });
    title.addEventListener('mouseout', function() {
      this.style.color = 'black';
    });
  });
  
  // Add hover effects to clickable project descriptions
  projectDescriptions.forEach(desc => {
    if (desc.onclick) {
      desc.style.cursor = 'pointer';
      desc.addEventListener('mouseover', function() {
        this.style.color = '#666';
      });
      desc.addEventListener('mouseout', function() {
        this.style.color = 'rgb(85, 85, 85)';
      });
    }
  });
});