document.addEventListener("DOMContentLoaded", function() {
    // Department Tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    const departmentPanes = document.querySelectorAll('.department-pane');
    
    tabButtons.forEach(button => {
      button.addEventListener('click', function() {
        // Remove active class from all buttons and panes
        tabButtons.forEach(btn => btn.classList.remove('active'));
        departmentPanes.forEach(pane => pane.classList.remove('active'));
        
        // Add active class to current button
        this.classList.add('active');
        
        // Show the corresponding department pane
        const tabId = this.getAttribute('data-tab');
        document.getElementById(`${tabId}-pane`).classList.add('active');
      });
    });
    
    // Testimonial Slider
    const testimonialSlides = document.querySelectorAll('.testimonial-slide');
    const testimonialDots = document.querySelectorAll('.dot');
    const prevButton = document.querySelector('.testimonial-prev');
    const nextButton = document.querySelector('.testimonial-next');
    let currentSlide = 0;
    
    function showSlide(index) {
      // Hide all slides
      testimonialSlides.forEach(slide => {
        slide.classList.remove('active');
      });
      
      // Remove active class from all dots
      testimonialDots.forEach(dot => {
        dot.classList.remove('active');
      });
      
      // Show the current slide and dot
      testimonialSlides[index].classList.add('active');
      testimonialDots[index].classList.add('active');
      
      // Update current slide index
      currentSlide = index;
    }
    
    // Next button click
    if (nextButton) {
      nextButton.addEventListener('click', function() {
        currentSlide = (currentSlide + 1) % testimonialSlides.length;
        showSlide(currentSlide);
      });
    }
    
    // Previous button click
    if (prevButton) {
      prevButton.addEventListener('click', function() {
        currentSlide = (currentSlide - 1 + testimonialSlides.length) % testimonialSlides.length;
        showSlide(currentSlide);
      });
    }
    
    // Dot click
    testimonialDots.forEach((dot, index) => {
      dot.addEventListener('click', function() {
        showSlide(index);
      });
    });
    
    // Auto slide every 5 seconds
    setInterval(function() {
      if (testimonialSlides.length > 0) {
        currentSlide = (currentSlide + 1) % testimonialSlides.length;
        showSlide(currentSlide);
      }
    }, 5000);
    
    // Mobile menu dropdown for department tabs
    const mobileWidth = 767;
    
    function checkScreenSize() {
      if (window.innerWidth <= mobileWidth) {
        // Add mobile class to department tabs
        document.querySelector('.department-tabs').classList.add('mobile-tabs');
      } else {
        document.querySelector('.department-tabs').classList.remove('mobile-tabs');
      }
    }
    
    // Check on load
    checkScreenSize();
    
    // Check on resize
    window.addEventListener('resize', checkScreenSize);
  });