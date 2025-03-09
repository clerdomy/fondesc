document.addEventListener("DOMContentLoaded", function() {
    // Step Navigation
    const steps = document.querySelectorAll('.step');
    const formSteps = document.querySelectorAll('.form-step');
    const nextButtons = document.querySelectorAll('.next-step');
    const prevButtons = document.querySelectorAll('.prev-step');
    
    // Next button click
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Find current active step
            const currentStep = document.querySelector('.form-step.active');
            const currentIndex = Array.from(formSteps).indexOf(currentStep);
            
            // Validate current step (simplified validation for demo)
            if (validateStep(currentIndex + 1)) {
                // Hide current step
                currentStep.classList.remove('active');
                
                // Show next step
                formSteps[currentIndex + 1].classList.add('active');
                
                // Update step indicators
                steps[currentIndex].classList.remove('active');
                steps[currentIndex + 1].classList.add('active');
                
                // Scroll to top of form
                document.querySelector('.registration-container').scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Previous button click
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Find current active step
            const currentStep = document.querySelector('.form-step.active');
            const currentIndex = Array.from(formSteps).indexOf(currentStep);
            
            // Hide current step
            currentStep.classList.remove('active');
            
            // Show previous step
            formSteps[currentIndex - 1].classList.add('active');
            
            // Update step indicators
            steps[currentIndex].classList.remove('active');
            steps[currentIndex - 1].classList.add('active');
            
            // Scroll to top of form
            document.querySelector('.registration-container').scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Course Type Change
    const courseTypeSelect = document.getElementById('course-type');
    const courseSelect = document.getElementById('course');
    
    if (courseTypeSelect && courseSelect) {
        courseTypeSelect.addEventListener('change', function() {
            // Clear current options
            courseSelect.innerHTML = '<option value="">Chwazi...</option>';
            
            // Add new options based on selected course type
            const courseType = this.value;
            
            if (courseType === 'undergraduate') {
                addCourseOption('administrasyon', 'Administrasyon');
                addCourseOption('analiz-sistem', 'Analiz ak Devlopman Sistèm');
                addCourseOption('pedagoji', 'Pedagoji');
                addCourseOption('kontabilite', 'Kontabilite');
                addCourseOption('maketing', 'Maketing');
            } else if (courseType === 'graduate') {
                addCourseOption('mba-jesyon', 'MBA nan Jesyon');
                addCourseOption('mba-finans', 'MBA nan Finans');
                addCourseOption('sikopedagoji', 'Sikopedagoji');
                addCourseOption('jesyon-pwoje', 'Jesyon Pwojè');
            } else if (courseType === 'technical') {
                addCourseOption('enfimye', 'Teknik nan Enfimyè');
                addCourseOption('enfomatik', 'Teknik nan Enfòmatik');
                addCourseOption('elektrisite', 'Teknik nan Elektrisite');
                addCourseOption('mekanik', 'Teknik nan Mekanik');
            } else if (courseType === 'free') {
                addCourseOption('excel', 'Excel Avanse');
                addCourseOption('angle', 'Anglè pou Biznis');
                addCourseOption('lidechip', 'Lidèchip ak Jesyon');
                addCourseOption('marketing-dijital', 'Maketing Dijital');
            }
        });
    }
    
    function addCourseOption(value, text) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        courseSelect.appendChild(option);
    }
    
    // Payment Method Change
    const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
    const paymentForms = document.querySelectorAll('.payment-form');
    
    paymentMethods.forEach(method => {
        method.addEventListener('change', function() {
            // Hide all payment forms
            paymentForms.forEach(form => {
                form.classList.add('hidden');
            });
            
            // Show selected payment form
            const selectedForm = document.getElementById(this.value + '-form');
            if (selectedForm) {
                selectedForm.classList.remove('hidden');
            }
        });
    });
    
    // FAQ Accordion
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const faqItem = this.parentElement;
            
            // Toggle active class
            faqItem.classList.toggle('active');
        });
    });
    
    // Form Validation (simplified for demo)
    function validateStep(stepNumber) {
        const currentStep = document.getElementById('step-' + stepNumber);
        const requiredFields = currentStep.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value) {
                isValid = false;
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });
        
        if (!isValid) {
            alert('Tanpri ranpli tout chan obligatwa yo.');
        }
        
        return isValid;
    }
    
    // Form Submission
    const registrationForm = document.getElementById('registration-form');
    
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            // In a real application, you would submit the form to the server
            // For demo purposes, we'll just show an alert
            
            // Uncomment this line to prevent the form from submitting
            // e.preventDefault();
            
            // alert('Enskripsyon ou soumèt avèk siksè! Nou pral kontakte ou byento.');
        });
    }
    
    // Set current year in footer
    const currentYearElement = document.getElementById('current-year');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }
});