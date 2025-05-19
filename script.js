function toggleMenu() {
  const menu = document.querySelector(".menu-links");
  const icon = document.querySelector(".hamburger-icon");
  menu.classList.toggle("open");
  icon.classList.toggle("open");
}
function openModal(filePath = './assests') {
  document.getElementById("readmeModal").style.display = "block";
  fetch(filePath)
    .then(response => response.text())
    .then(data => {
      document.getElementById("readme-text").innerHTML = marked.parse(data);
    })
    .catch(error => {
      document.getElementById("readme-text").textContent = "Error loading README.";
      console.error(error);
    });
}

function closeModal() {
  document.getElementById("readmeModal").style.display = "none";
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeModal();
  }
  
});

