// Initialize functionality when DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Set current year in footer
    document.getElementById("current-year").textContent = new Date().getFullYear()
  
    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById("mobile-menu-toggle")
    const mobileMenu = document.getElementById("mobile-menu")
  
    if (mobileMenuToggle && mobileMenu) {
      mobileMenuToggle.addEventListener("click", () => {
        mobileMenu.classList.toggle("active")
        mobileMenuToggle.querySelector("i").classList.toggle("fa-bars")
        mobileMenuToggle.querySelector("i").classList.toggle("fa-times")
      })
    }
  
    // Search toggle
    const searchToggle = document.getElementById("search-toggle")
    const searchBar = document.getElementById("search-bar")
  
    if (searchToggle && searchBar) {
      searchToggle.addEventListener("click", () => {
        searchBar.classList.toggle("active")
      })
    }
  
    // Mobile dropdowns
    const mobileDropdowns = document.querySelectorAll(".mobile-dropdown-header")
  
    mobileDropdowns.forEach((dropdown) => {
      dropdown.addEventListener("click", function () {
        // Toggle the active class on the next sibling (dropdown content)
        this.nextElementSibling.classList.toggle("active")
        // Toggle the icon rotation
        this.querySelector("i").classList.toggle("fa-chevron-down")
        this.querySelector("i").classList.toggle("fa-chevron-up")
      })
    })
  })
  
  