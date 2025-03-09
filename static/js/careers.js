document.addEventListener("DOMContentLoaded", function() {
    // Video Play Button
    const videoPlayButton = document.querySelector('.video-play-button');
    const videoPlaceholder = document.querySelector('.video-placeholder');
    
    if (videoPlayButton && videoPlaceholder) {
      videoPlayButton.addEventListener('click', function() {
        // Replace image with video
        const videoContainer = this.parentElement;
        const videoIframe = document.createElement('iframe');
        videoIframe.setAttribute('src', 'https://www.youtube.com/embed/VIDEO_ID?autoplay=1');
        videoIframe.setAttribute('frameborder', '0');
        videoIframe.setAttribute('allowfullscreen', 'true');
        videoIframe.setAttribute('width', '100%');
        videoIframe.setAttribute('height', '100%');
        videoIframe.style.position = 'absolute';
        videoIframe.style.top = '0';
        videoIframe.style.left = '0';
        videoIframe.style.width = '100%';
        videoIframe.style.height = '100%';
        
        // Remove placeholder and play button
        videoPlaceholder.remove();
        this.remove();
        
        // Add iframe
        videoContainer.appendChild(videoIframe);
        videoContainer.style.paddingBottom = '56.25%'; // 16:9 aspect ratio
        videoContainer.style.height = '0';
      });
    }
    
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
    
    // Job Filters
    const departmentFilter = document.getElementById('department-filter');
    const typeFilter = document.getElementById('type-filter');
    const locationFilter = document.getElementById('location-filter');
    const jobCards = document.querySelectorAll('.job-card');
    const noJobsMessage = document.querySelector('.no-jobs-message');
    const resetFiltersButton = document.getElementById('reset-filters');
    
    function filterJobs() {
      const department = departmentFilter.value;
      const type = typeFilter.value;
      const location = locationFilter.value;
      
      let visibleJobs = 0;
      
      jobCards.forEach(card => {
        const cardDepartment = card.getAttribute('data-department');
        const cardType = card.getAttribute('data-type');
        const cardLocation = card.getAttribute('data-location');
        
        const departmentMatch = department === 'all' || cardDepartment === department;
        const typeMatch = type === 'all' || cardType === type;
        const locationMatch = location === 'all' || cardLocation === location;
        
        if (departmentMatch && typeMatch && locationMatch) {
          card.style.display = 'block';
          visibleJobs++;
        } else {
          card.style.display = 'none';
        }
      });
      
      // Show or hide no jobs message
      if (visibleJobs === 0) {
        noJobsMessage.style.display = 'block';
      } else {
        noJobsMessage.style.display = 'none';
      }
    }
    
    // Add event listeners to filters
    if (departmentFilter) {
      departmentFilter.addEventListener('change', filterJobs);
    }
    
    if (typeFilter) {
      typeFilter.addEventListener('change', filterJobs);
    }
    
    if (locationFilter) {
      locationFilter.addEventListener('change', filterJobs);
    }
    
    // Reset filters
    if (resetFiltersButton) {
      resetFiltersButton.addEventListener('click', function() {
        departmentFilter.value = 'all';
        typeFilter.value = 'all';
        locationFilter.value = 'all';
        filterJobs();
      });
    }
    
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
      const question = item.querySelector('.faq-question');
      
      question.addEventListener('click', function() {
        // Toggle active class on clicked item
        item.classList.toggle('active');
        
        // Close other items
        faqItems.forEach(otherItem => {
          if (otherItem !== item) {
            otherItem.classList.remove('active');
          }
        });
      });
    });
    
    // Pagination
    const paginationPrev = document.querySelector('.pagination-prev');
    const paginationNext = document.querySelector('.pagination-next');
    const pageNumbers = document.querySelectorAll('.page-number');
    
    pageNumbers.forEach(number => {
      number.addEventListener('click', function() {
        // Remove active class from all page numbers
        pageNumbers.forEach(num => {
          num.classList.remove('active');
        });
        
        // Add active class to clicked page number
        this.classList.add('active');
        
        // Enable/disable prev/next buttons
        if (this.textContent === '1') {
          paginationPrev.classList.add('disabled');
        } else {
          paginationPrev.classList.remove('disabled');
        }
        
        if (this.textContent === pageNumbers.length.toString()) {
          paginationNext.classList.add('disabled');
        } else {
          paginationNext.classList.remove('disabled');
        }
        
        // Scroll to top of job listings
        document.querySelector('.job-listings').scrollIntoView({ behavior: 'smooth' });
      });
    });
    
    if (paginationPrev) {
      paginationPrev.addEventListener('click', function() {
        if (!this.classList.contains('disabled')) {
          const activePage = document.querySelector('.page-number.active');
          const prevPage = activePage.previousElementSibling;
          
          if (prevPage) {
            prevPage.click();
          }
        }
      });
    }
    
    if (paginationNext) {
      paginationNext.addEventListener('click', function() {
        if (!this.classList.contains('disabled')) {
          const activePage = document.querySelector('.page-number.active');
          const nextPage = activePage.nextElementSibling;
          
          if (nextPage) {
            nextPage.click();
          }
        }
      });
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
          targetElement.scrollIntoView({
            behavior: 'smooth'
          });
        }
      });
    });
  });