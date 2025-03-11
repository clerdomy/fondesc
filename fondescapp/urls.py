from django.urls import path
from fondescapp import views

# Lista de padrões de URL do aplicativo 'fondescapp'
urlpatterns = [
    # --- Páginas principais ---
    path('', views.home, name='home-page'),                          # Página inicial
    path('kou/', views.courses, name='courses-page'),                # Lista de cursos
    path('kou/<str:course_type>/detay/', views.course_detail, name='course-detail-page'),  # Detalhes de um curso
    path('inskripsyon/', views.registration_view, name='register-page'),  # Página de inscrição

    # --- Sobre nós ---
    path('sou-nou/kimoun-nou-ye', views.about, name='about-page'),  # Sobre nós
    path('sou-nou/metodoloji', views.metodoloji_page, name='metodoloji'),  # Metodologia
    path('sou-nou/pwofesè-yo', views.info_about_teacher, name='teacher-page'),  # Professores

    # --- Contato e interação ---
    path('contact/', views.contact, name='contact-page'),            # Página de contato
    path('contact/submit/', views.contact_submit, name='contact_submit'),  # Envio de formulário de contato
    path('travay-avek-nou/', views.work_with_us, name='work-with-us-page'),  # Trabalhe conosco
    path('subscribe/', views.subscribe, name='subscribe'),           # Subscrição (ex.: newsletter)

    # --- Informações adicionais ---
    path('faq/', views.faq_page, name='faq'),                        # Perguntas frequentes
    path('bous-detid/', views.scholarships_page, name='scholarships'),  # Bolsas de estudo
    path('bous-detid/enskri/', views.scholarship_interest, name='scholarship_interest'),  # Interesse em bolsas
    path('kondisyon-itilizasyon/', views.terms_of_use, name='terms_of_use'),  # Termos de uso
    path('politik-konfidansyalite/', views.privacy_policy, name='privacy_policy'),  # Política de privacidade

    # --- Autenticação ---
    path('konekte/', views.login_view, name='login-page'),           # Página de login
    path('dekonekte/', views.logout_view, name='logout-page'),             # Logout 

    # --- Páginas temporárias ---
    path('under_development/', views.under_development, name='under_development'),  # Em desenvolvimento
]