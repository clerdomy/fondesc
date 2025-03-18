document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });
    }
    
    // Mobile dropdown toggles
    const mobileDropdowns = document.querySelectorAll('.mobile-dropdown-header');
    
    mobileDropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function() {
            this.parentElement.classList.toggle('active');
        });
    });
    
    // Course progress tracking
    const lessonCompleteButtons = document.querySelectorAll('.mark-complete-btn');
    
    lessonCompleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const lessonId = this.dataset.lessonId;
            const progressBar = document.querySelector('.course-progress-bar');
            const progressText = document.querySelector('.progress-text');
            
            // Send AJAX request to mark lesson as complete
            fetch(`/courses/lesson/${lessonId}/complete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    this.innerHTML = '<i class="fas fa-check-circle"></i> Completed';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    this.disabled = true;
                    
                    // Update progress bar if it exists
                    if (progressBar && progressText) {
                        progressBar.style.width = `${data.progress}%`;
                        progressText.textContent = `${data.progress}%`;
                    }
                    
                    // Add completed class to lesson in sidebar
                    const sidebarItem = document.querySelector(`.lesson-link[data-lesson-id="${lessonId}"]`);
                    if (sidebarItem) {
                        sidebarItem.classList.add('completed');
                        const icon = sidebarItem.querySelector('.lesson-icon');
                        if (icon) {
                            icon.classList.remove('fa-circle');
                            icon.classList.add('fa-check-circle');
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
    
    // Quiz functionality
    const quizForm = document.getElementById('quiz-form');
    
    if (quizForm) {
        const answerOptions = document.querySelectorAll('.answer-option');
        
        answerOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Deselect other options in the same question
                const questionId = this.dataset.questionId;
                const questionOptions = document.querySelectorAll(`.answer-option[data-question-id="${questionId}"]`);
                
                questionOptions.forEach(opt => {
                    opt.classList.remove('selected');
                    opt.querySelector('input[type="radio"]').checked = false;
                });
                
                // Select this option
                this.classList.add('selected');
                this.querySelector('input[type="radio"]').checked = true;
            });
        });
    }
    
    // Video player functionality
    const videoContainers = document.querySelectorAll('.video-container');
    
    videoContainers.forEach(container => {
        // Add responsive behavior if needed
    });
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Set current year in footer
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
});

// Responsive adjustments
window.addEventListener('resize', function() {
    // Add responsive adjustments if needed
});
